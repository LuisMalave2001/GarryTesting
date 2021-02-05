odoo.define('pos_pr.components.reports', function (require) {
    'use strict';

    const BaseWidget = require('point_of_sale.BaseWidget');
    const core = require('web.core');
    const gui = require('point_of_sale.gui');

    const QWeb = core.qweb;
    const _t = core._t;

    const InvoicePaymentReceiptment = BaseWidget.extend({
        template: 'InvoicePaymentReceipt',

        /**
         * This will be used to render payments receipts in POS.
         * @param {Object} parent The current parent
         * @param {Object} options Widget's options
         * @param {PaymentGroup} options.paymentGroup The payment group to rendered
         * @param {Object} options.customer The customer to rendered
         * @param {Boolean=false} options.copy The customer to rendered
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);

            // Attributes by options
            this.paymentGroup = options.paymentGroup || {};
            this.customer = options.customer || {};
            this.copy = !!options.copy;

            // Default attributes
            this.company = this.pos.company;
            Object.defineProperty(this, 'invoices', {get: this._compute_invoice});
            Object.defineProperty(this, 'discount_total', {get: this._compute_discount_total});
            Object.defineProperty(this, 'payments_by_invoice', {get: this._compute_payments_by_invoice});
            Object.defineProperty(this, 'payment_totals_by_method', {get: this._compute_payment_totals_by_method});
            Object.defineProperty(this, 'payment_methods', {get: this._compute_payment_methods});
        },

        /**
         * @override
         */
        renderElement: function () {
            this._super.apply(this, arguments);

            if (this.copy) {
                const copyText = _t('COPY');
                const svgTextImage = `<svg xmlns='http://www.w3.org/2000/svg' version='1.1'  x='0px' y='0px' width='595.28px' height='841.89px' viewBox='0 0 595.28 841.89' enable-background='new 0 0 595.28 841.89' xml:space='preserve'><text fill='#009DE0' font-weight='bold' font-size='200' font-family="Arial, Helvetica, sans-serif" text-anchor='middle' transform='translate(350, 480) rotate(-45)'>${copyText}</text></svg>`;
                const backgroundCopyImageSVG = `url(data:image/svg+xml;base64,${btoa(svgTextImage)})`;
                this.el.style.setProperty('background-image', backgroundCopyImageSVG, 'important');
                //
                // this.$el.css({
                //     'background-image': backgroundCopyImageSVG
                // });
            }
        },

        _compute_invoice: function () {
            const invoices = [];
            _.each(this.paymentGroup.invoice_payment_ids, (invoicePayment) => {
                if (!invoices.some(invoice => invoice.id === invoicePayment.move_id.id)) {
                    if (!invoicePayment.move_id.amount_total) {
                        invoicePayment.move_id = this.pos.db.due_invoices_by_id[invoicePayment.move_id.id]
                    }
                    invoices.push(invoicePayment.move_id);
                }
            });
            return invoices;
        },

        _compute_discount_total: function () {
            let discountTotal = 0;
            _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
                if (invoicePayment.state !== 'cancelled') {
                    discountTotal += invoicePayment.discount_amount || 0;
                }
            });
            return discountTotal;
        },

        _compute_payment_methods: function () {
            const paymentMethods = [];
            _.each(this.paymentGroup.invoice_payment_ids, invoicePayment => {
                if (invoicePayment.payment_method_id.id !== this.pos.db.discount_payment_method.id
                    && !paymentMethods.some(paymentMethod => paymentMethod.id === invoicePayment.payment_method_id.id)) {
                    paymentMethods.push(invoicePayment.payment_method_id);
                }
            });
            return paymentMethods;
        },

        _compute_payments_by_invoice: function () {
            const paymentsByInvoice = {};
            _.each(this.paymentGroup.invoice_payment_ids, invoicePayment => {
                if (invoicePayment.payment_method_id.id !== this.pos.db.discount_payment_method.id) {
                    const invoicePaymentInvoice = invoicePayment.move_id;
                    if (!paymentsByInvoice[invoicePaymentInvoice.id]) {
                        paymentsByInvoice[invoicePaymentInvoice.id] = [];
                    }
                    paymentsByInvoice[invoicePaymentInvoice.id].push(invoicePayment);
                }
            });
            return paymentsByInvoice;
        },

        _compute_payment_totals_by_method: function () {
            const paymentTotalsByMethod = {};
            _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
                const paymentMethod = invoicePayment.payment_method_id;
                if (!paymentTotalsByMethod[paymentMethod.id]) {
                    paymentTotalsByMethod[paymentMethod.id] = 0;
                }
                if (invoicePayment.state !== 'cancelled') {
                    paymentTotalsByMethod[paymentMethod.id] += invoicePayment.payment_amount;
                }
            });
            return paymentTotalsByMethod;
        }
    });

    const SurchargePaymentReceiptment = BaseWidget.extend({
        template: 'PosPr.SurchargePaymentReceipt',

        /**
         * This will be used to render payments receipts in POS.
         * @param {Object} parent The current parent
         * @param {Object} options Widget's options
         * @param {Object} options.surcharge The surcharge to rendered
         * @param {Object} options.customer The customer to rendered
         * @param {Object} options.copy Check if there is watermark
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);

            // Attributes by options
            this.surcharge = options.surcharge || {};
            this.customer = options.customer || {};
            this.copy = !!options.copy;

            // Default attributes
            this.company = this.pos.company;
            this.invoices = this.surcharge.move_ids || [];
            // Object.defineProperty(this, 'invoices', {get: this._compute_invoice});
            // Object.defineProperty(this, 'payments_by_invoice', {get: this._compute_payments_by_invoice});
            // Object.defineProperty(this, 'payment_totals_by_method', {get: this._compute_payment_totals_by_method});
            // Object.defineProperty(this, 'payment_methods', {get: this._compute_payment_methods});
        },

        /**
         * @override
         */
        renderElement: function () {
            this._super.apply(this, arguments);

            const copyText = _t('COPY');
            const backgroundCopyImageSVG = `url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' version='1.1'  x='0px' y='0px' width='595.28px' height='841.89px' viewBox='0 0 595.28 841.89' enable-background='new 0 0 595.28 841.89' xml:space='preserve'><text fill='#009DE0' font-weight='bold' font-size='200' text-anchor='middle' transform='translate(350, 480) rotate(-45)'>${copyText}</text></svg>)`;
            this.el.style.setProperty('background-image', backgroundCopyImageSVG, 'important');
        }

        // _compute_invoice: function () {
        //     const invoices = [];
        //     _.each(this.surcharge.move_ids, (moveId) => {
        //         if (!invoices.some(invoice => invoice.id === moveId)) {
        //             const surchargeAuxPaidInvoice = this.pos.db.due_invoices_by_id[moveId];
        //             invoices.push(surchargeAuxPaidInvoice);
        //         }
        //     });
        //     return invoices;
        // },
        //
        // _compute_payment_methods: function () {
        //     const paymentMethods = [];
        //     _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
        //         if (!paymentMethods.some(paymentMethod => paymentMethod.id === invoicePayment.payment_method_id.id)) {
        //             paymentMethods.push(invoicePayment.payment_method_id);
        //         }
        //     });
        //     return paymentMethods;
        // },
        //
        // _compute_payments_by_invoice: function () {
        //     const paymentsByInvoice = {};
        //     _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
        //
        //         const invoicePaymentInvoice = invoicePayment.move_id;
        //         if (!paymentsByInvoice[invoicePaymentInvoice.id]) {
        //             paymentsByInvoice[invoicePaymentInvoice.id] = [];
        //         }
        //         paymentsByInvoice[invoicePaymentInvoice.id].push(invoicePayment);
        //     });
        //     return paymentsByInvoice;
        // },
        //
        // _compute_payment_totals_by_method: function () {
        //     const paymentTotalsByMethod = {};
        //     _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
        //
        //         const paymentMethod = invoicePayment.payment_method_id;
        //         if (!paymentTotalsByMethod[paymentMethod.id]) {
        //             paymentTotalsByMethod[paymentMethod.id] = 0;
        //         }
        //         paymentTotalsByMethod[paymentMethod.id] += invoicePayment.payment_amount;
        //     });
        //     return paymentTotalsByMethod;
        // }
    });
    return {
        InvoicePaymentReceiptment,
        SurchargePaymentReceiptment,
    };

});
