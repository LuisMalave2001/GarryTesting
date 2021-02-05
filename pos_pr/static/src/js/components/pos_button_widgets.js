odoo.define('pos_pr.components.buttons', function (require) {
    'use strict';

    const chrome = require("point_of_sale.chrome");

    let PaymentRegisterButtonWidget = chrome.HeaderButtonWidget.extend({
        /**
         * Original init function overwrite our action function
         * @param parent
         * @param options
         */
        init: function (parent, options) {
            options.action = this.action;
            this._super.apply(this, arguments);
        },

        renderElement: function () {
            this._super.apply(this, arguments);
            this.$el.addClass('oe_status');
        },

        /**
         * Inherited method: this fire up when the button is clicked
         */
        action: function () {
            this._go_to_register_payment_screen();
        },

        _go_to_register_payment_screen: function () {
            // var self = this;
            this.gui.show_screen("invoice_payment_register_screen");
        },
    });

    // screens.define_action_button({'name': 'goToRegisterPaymentScreen', 'widget': BtnRegisterPayment});
    return {
        "PaymentRegisterButtonWidget": PaymentRegisterButtonWidget
    };
});
