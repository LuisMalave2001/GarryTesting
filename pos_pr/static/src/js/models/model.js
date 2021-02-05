odoo.define('pos_pr.models', function (require) {
    let models = {};

    const EduwebClass = require('eduweb_utils.Class');

    const exportAsJSON = function (object, fields) {
        const jsonObject = {};
        for (const field of fields) {
            jsonObject[field] = object[field];
        }
        return jsonObject;
    };

    const initAsJSON = function (object, fields, json) {
        for (const field of fields) {
            object[field] = json[field];
        }
    };

    models.AccountMove = EduwebClass.extend({
        fields: [
            {name: 'id', type: 'integer'},

            {name: 'name', type: 'char'},

            {name: 'amount_total', type: 'float'},
            {name: 'amount_residual', type: 'float'},
            {name: 'session_payment', type: 'float'},
            {name: 'expected_final_due', type: 'float'},
            {name: 'pos_pr_paid_amount', type: 'float'},
            {name: 'surcharge_amount', type: 'float'},

            {name: 'invoice_date', type: 'date'},
            {name: 'invoice_date_due', type: 'date'},

            {name: 'partner_id', type: 'many2one'},
            {name: 'journal_id', type: 'many2one'},

            {name: 'invoice_line_ids', type: 'one2many'},
        ],
    });

    models.AccountMoveLine = EduwebClass.extend({
        fields: [
            {name: 'id', type: 'integer'},
            {name: 'name', type: 'char'},

            {name: 'price_unit', type: 'float'},
            {name: 'quantity', type: 'float'},
            {name: 'discount', type: 'float'},
            {name: 'price_subtotal', type: 'float'},
            {name: 'price_total', type: 'float'},

            {name: 'tax_ids', type: 'many2many'},
            {name: 'product_id', type: 'many2one'},
            {name: 'move_id', type: 'many2one'},
        ]
    });

    models.InvoicePayment = EduwebClass.extend({
        fields: [
            {name: 'id', type: 'integer'},
            {name: 'name', type: 'char'},
            {name: 'state', type: 'char'},

            {name: 'payment_amount', type: 'float'},
            {name: 'discount_amount', type: 'float'},

            {name: 'date', type: 'date'},
            {name: 'payment_method_id', type: 'many2one'},
            {name: 'pos_session_id', type: 'many2one'},
            {name: 'move_id', type: 'many2one'},
            {name: 'invoice_address_id', type: 'many2one'},
        ],
    });

    models.SurchargeInvoice = EduwebClass.extend({
        fields: [
            {name: 'move_ids', type: 'many2many'},
            {name: 'payment_ids', type: 'many2many'},
            {name: 'amount', type: 'integer', default: 0},
            {name: 'free_of_surcharge', type: 'integer', default: 0},
            {name: 'date', type: 'date'},
        ],
    });

    models.PaymentRegisterPadState = Backbone.Model.extend({
        constructor: function (payment_method_ids) {
            this.surcharger_amount = 0;
            this.payment_method_ids = payment_method_ids;
            this.payment_amount_by_method_id = {};
            this._generate_paymenta_amounts();
        },

        _generate_paymenta_amounts: function () {
            _.each(this.payment_method_ids, payment_method_id => {
                this.payment_amount_by_method_id[payment_method_id.id] = 0;
            });
        },

    });

    models.PaymentGroup = EduwebClass.extend({
        fields: [
            {name: 'id', type: 'integer'},
            {name: 'name', type: 'char'},
            {name: 'invoice_payment_ids', type: 'one2many'},

            {name: 'payment_amount_total', type: 'compute', method: '_getPaymentAmountTotal'},
            {name: 'payment_change', type: 'float'},
            {name: 'date', type: 'char'},

            {name: 'pos_session_id', type: 'many2one'},
            {name: 'partner_id', type: 'many2one'},
        ],

        _getPaymentAmountTotal: function () {
            let paymentAmountTotal = 0;
            _.each(this.invoice_payment_ids, function (invoicePayment) {
                if (invoicePayment.state !== 'cancelled') {
                    paymentAmountTotal += invoicePayment.payment_amount || 0;
                }
            });
            return paymentAmountTotal;
        }
    });

    models.PaymentRegisterState = Backbone.Model.extend({});

    return models;

});
