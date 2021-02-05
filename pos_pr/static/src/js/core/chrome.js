odoo.define('pos_pr.core.chrome', function (require) {
    const core = require('web.core');
    const chrome = require('point_of_sale.chrome');
    const posPrButtons = require('pos_pr.components.buttons');
    const _lt = core._lt;

    const PaymentRegisterButtonWidget = posPrButtons.PaymentRegisterButtonWidget;

    const SynchInvoicePaymentWidget = chrome.StatusWidget.extend({
        // status: ['connected','connecting','disconnected','warning','error']
        template: 'SynchInvoicePaymentWidget',

        event: _.extend({}, chrome.StatusWidget.event, {
            'click': 'synch_invoice_payments',
        }),

        renderElement: function () {
            this._super.apply(this, arguments);
            const pendingInvoicePayments = this.pos.db.load('pending_invoice_payments', []);
            const pendingSurchargeInvoices = this.pos.db.load('pending_surcharge_invoices', []);

            const pendingPaymentsCount = pendingInvoicePayments.length + pendingSurchargeInvoices.length;

            if (pendingPaymentsCount > 0) {
                this.set_status('warning', pendingPaymentsCount);
            }

        },

        start: function () {
            const self = this;
            this._super.apply(this, arguments);
            this.pos.bind('invoice_payment:synch', function (synch) {
                self.set_status(synch.state, synch.pending);
            });

            this.$el.on('click', this.synch_invoice_payments.bind(this));
        },

        /**
         * Sych point of sale invoice payments with server
         */
        synch_invoice_payments: function () {
            this.pos.synch_invoive_payment_and_surcharges();
        }
    });

    chrome.Chrome.include({

        /**
         * We add our button here
         * @override
         */
        build_widgets: function () {
            const self = this;
            this.widgets.some(function (widget, index) {
                if (widget.name === 'notification') {
                    self.widgets.splice(index, 0, self.synch_invoice_payment_widget);
                    self.widgets.splice(index, 0, self.payment_register_button_widget);
                    return true;
                }
                return false;
            });
            this._super.apply(this, arguments);
        },

        /**
         * Builds an object with the right format for this.widgets that creates
         * the resend invoice payment button
         * @private
         */
        synch_invoice_payment_widget: {
            'name': 'synch_invoice_payment',
            'widget': SynchInvoicePaymentWidget,
            'append': '.pos-rightheader',
        },

        /**
         *
         */
        payment_register_button_widget: {
            'name': 'payment_register_button',
            'widget': PaymentRegisterButtonWidget,
            'append': '.pos-branding',
            'args': {
                label: _lt('Payment register'),
            }
        },
    });

    return {
        'SynchInvoicePaymentWidget': SynchInvoicePaymentWidget,
    };

});
