odoo.define("pos_pr.load_data.models", require => {

    const models = require("point_of_sale.models")
    const PosDB = require("point_of_sale.DB")
    const posPrModels = require("pos_pr.models")

    models.load_models([
        {
            model: "account.journal",
            fields: ["display_name", "inbound_payment_method_ids"],
            domain: [],
            loaded(self, journals) {
                self.db.add_journals(journals);
            }
        }
    ]);
    models.load_models([
        {
            model: "account.move",
            fields: [
                "name",
                "journal_id",
                "partner_id",
                "invoice_date",
                "invoice_date_due",
                "amount_total",
                "amount_residual",
                "surcharge_invoice_id",
                "is_overdue",
                "surcharge_amount",
                "pos_pr_paid_amount",
                'invoice_line_ids',
            ],
            domain: [
                ["type", "=", "out_invoice"],
                ["invoice_payment_state", "!=", "paid"],
                ["state", "=", "posted"],
                ["partner_id", "!=", false],
            ],
            order: [{name: 'invoice_date_due', asc: true}], //, (name) { return {name: name}; }) =>,
            loaded(self, invoices) {
                self.db.add_due_invoices(invoices);
            }
        }
    ]);

    models.load_models([
        {
            model: 'account.move.line',
            fields: [
                'move_id',
                'product_id',
                'name',
                'quantity',
                'price_unit',
                'discount',
                'tax_ids',
                'price_subtotal',
                'price_total',
            ],
            domain: self => [['move_id', 'in', self.db.due_invoices_ids], ['exclude_from_invoice_tab', '=', false]],
            loaded: (self, invoiceLineIds) => {
                self.add_due_invoice_lines(invoiceLineIds);
            }
        }
    ])

    models.load_models([
        {
            model: "pos.payment.method",
            fields: ["id", "name"],
            domain: [
                ["is_pos_pr_discount", "=", true]
            ],
            loaded(self, posPaymentMethods) {
                if (posPaymentMethods && posPaymentMethods.length > 0) {
                    self.db.discount_payment_method = posPaymentMethods[0];
                }
            }
        }
    ]);

    models.load_models([
        {
            model: "pos_pr.invoice.payment",
            fields: ["id", "name"],
            domain(self) {
                return [['id', 'in', self.pos_session.invoice_payment_ids]];
            },
            loaded(self, invoicePayments) {
                self.db.add_invoice_payments(invoicePayments);
            }
        }
    ]);

    models.load_models([
        {
            model: "pos_pr.invoice.payment",
            fields: [
                'id',
                'name',
                'payment_amount',
                'discount_amount',
                'date',
                'payment_method_id',
                'pos_session_id',
                'move_id',
                'invoice_address_id',
                'state',
            ],
            domain(self) {
                return [['id', 'in', self.pos_session.invoice_payment_ids]];
            },
            loaded(self, invoicePayments) {
                self.db.add_invoice_payments(invoicePayments);
            }
        }
    ]);

    models.load_models([
        {
            model: "pos_pr.payment_group",
            fields: [
                'id',
                'name',
                'invoice_payment_ids',
                'payment_amount_total',
                'payment_change',
                'date',
                'pos_session_id',
                'partner_id',
            ],
            domain(self) {
                return [['id', 'in', self.pos_session.invoice_payment_groups_ids]];
            },
            loaded(self, invoicePayments) {
                self.db.add_invoice_payment_groups(invoicePayments);
            }
        }
    ]);

    PosDB.include({
        init(options) {
            this._super(options);
            this.journal = [];
            this.journal_by_id = {};

            this.due_invoices = [];
            this.due_invoices_by_id = {};
            this.due_invoices_ids = [];

            this.due_invoice_lines = [];
            this.due_invoice_lines_by_id = {};

            this.invoice_payments = [];
            this.invoice_payments_by_id = {};

            this.invoice_payment_groups = [];
            this.invoice_payment_groups_by_id = {};
        },

        add_journals(add_journals) {
            this.journals = add_journals;
            let self = this;
            _.each(add_journals, journal => {
                self.journal_by_id[journal.id] = journal;
            });
        },

        add_due_invoices(invoices) {
            _.each(invoices, invoiceJson => {
                const invoice = new posPrModels.AccountMove(invoiceJson);

                invoice.amount_residual -= invoice.pos_pr_paid_amount;

                invoice.expected_final_due = invoice.amount_residual;
                invoice.original_surcharge = invoice.surcharge_amount;
                invoice.session_payment = 0;
                invoice.discount_amount = 0;
                this.due_invoices.push(invoice);
                this.due_invoices_by_id[invoice.id] = invoice;

                this.due_invoices_ids.push(invoice.id);

            });
        },

        add_invoice_payments(invoicePayments) {
            this.invoice_payments = [];
            _.each(invoicePayments, paymentJson => {
                const payment = new posPrModels.InvoicePayment(paymentJson);
                this.invoice_payments.push(payment);
                this.invoice_payments_by_id[payment.id] = payment;
            });
        },

        add_invoice_payment_groups(invoicePaymentGroups) {
            this.invoice_payment_groups = [];
            _.each(invoicePaymentGroups, paymentGroupJson => {
                const paymentGroup = new posPrModels.PaymentGroup(paymentGroupJson);
                this.invoice_payment_groups.push(paymentGroup);
                this.invoice_payment_groups_by_id[paymentGroup.id] = paymentGroup;

                const invoice_payments = [];
                _.each(paymentGroup.invoice_payment_ids, invoicePaymentId => {
                    const payment = this.invoice_payments_by_id[invoicePaymentId];
                    invoice_payments.push(payment);
                });
                paymentGroup.invoice_payment_ids = invoice_payments;
            });
        },

    });

    models.load_fields('pos.session', ['invoice_surcharge_ids', 'invoice_payment_ids', 'invoice_payment_groups_ids']);
    models.load_fields('res.company', ['city', 'street', 'parent_id']);
    models.load_fields('res.partner', ['person_type', 'family_ids', 'member_ids', 'student_invoice_address_ids']);

    models.PosModel = models.PosModel.extend({

        add_due_invoice_lines(invoiceLines) {
            _.each(invoiceLines, invoiceLineJSON => {
                const invoiceLine = new posPrModels.AccountMoveLine(invoiceLineJSON);

                invoiceLine.taxes = [];
                _.each(invoiceLine.tax_ids, tax_id => {
                    invoiceLine.taxes.push(this.taxes_by_id[tax_id]);
                });
                invoiceLine.taxes_joined = _.map(invoiceLine.taxes, tax => `"${tax.name}"`).join(', ');
                this.db.due_invoice_lines.push(invoiceLine);
                this.db.due_invoice_lines_by_id[invoiceLine.id] = invoiceLine;

                const move = this.db.due_invoices_by_id[invoiceLine.move_id.id];
                if (!move.invoice_lines) {
                    move.invoice_lines = [];
                }
                move.invoice_lines.push(invoiceLine);
            });
        },

        /**
         * Get the tCurrent number in the payment sequence
         * @param {Boolean} reset Reset the payment sequence
         */
        getCurrentPaymentSequenceNumber(reset) {
            reset = !!reset;
            let paymentSequenceNumber = parseInt(this.db.load('payment_sequence_number', 0));
            if (!paymentSequenceNumber || reset) {
                paymentSequenceNumber = this.pos_session.invoice_payment_ids.length;
            }
            this.db.save('payment_sequence_number', paymentSequenceNumber);
            return paymentSequenceNumber;
        },

        /**
         * Get the next number in the payment sequence
         * @param {Boolean} [reset] Reset the payment sequence
         */
        getNextPaymentSequenceNumber(reset) {
            reset = !!reset;
            const nextNumber = this.getCurrentPaymentSequenceNumber(reset) + 1;
            this.db.save('payment_sequence_number', nextNumber);
            return nextNumber;
        },


        /**
         * Get the tCurrent number in the payment group sequence
         * @param {Boolean} reset Reset the payment group sequence
         */
        getCurrentPaymentGroupSequenceNumber(reset) {
            reset = !!reset;
            let paymentSequenceNumber = parseInt(this.db.load('payment_group_sequence_number', 0));

            if (!paymentSequenceNumber || reset) {
                paymentSequenceNumber = this.pos_session.invoice_payment_groups_ids.length;
            }
            this.db.save('payment_group_sequence_number', paymentSequenceNumber);
            return paymentSequenceNumber;

        },

        /**
         * Get the next number in the payment group sequence
         * @param {Boolean} [reset] reset Reset the payment group sequence
         */
        getNextPaymentGroupSequenceNumber(reset) {
            reset = !!reset;
            const nextNumber = this.getCurrentPaymentGroupSequenceNumber(reset) + 1;
            this.db.save('payment_group_sequence_number', nextNumber);
            return nextNumber;
        },

        generateNextPaymentNumber() {
            const nextNumber = this.getNextPaymentSequenceNumber();
            return 'POS-P/'
                + this._zero_pad(this.pos_session.id, 5) + '-'
                + this._zero_pad(this.pos_session.login_number, 3) + '/'
                + this._zero_pad(nextNumber, 5);
        },

        generateNextPaymentGroupNumber() {
            const nextNumber = this.getNextPaymentGroupSequenceNumber();
            return 'POS-PG/'
                + this._zero_pad(this.pos_session.id, 5) + '-'
                + this._zero_pad(this.pos_session.login_number, 3) + '/'
                + this._zero_pad(nextNumber, 5);
        },

        _zero_pad(num, size) {
            let s = "" + num;
            while (s.length < size) {
                s = "0" + s;
            }
            return s;
        },

        /**
         * Get the company with a specific format
         */
        getFormattedCompanyAddress() {

            let formattedCompanyAddress = "";
            if (this.company.country) {
                formattedCompanyAddress += this.company.country.name + ', ';
            }
            if (this.company.state_id) {
                formattedCompanyAddress += this.company.state_id[1] + ', ';
            }
            if (this.company.city) {
                formattedCompanyAddress += this.company.city + ', ';
            }
            if (this.company.street) {
                formattedCompanyAddress += this.company.street;
            }
            formattedCompanyAddress = formattedCompanyAddress.trim().replace('/,$/', '');
            return formattedCompanyAddress;
        }
    });

})