odoo.define('pos_pr.payment_register.screens', function (require) {

    const screens = require("point_of_sale.screens");
    const gui = require("point_of_sale.gui");
    const {PosPRScreen, InvoicePaymentListScreen} = require('pos_pr.owl.components');
    // Invoices screen
    const InvoicePaymentRegisterScreenWidget = screens.ScreenWidget.extend({

        events: {
            'click .back': '_go_to_back_screen',
            'click .payment_list': '_go_to_payment_list_screen',
        },

        back_screen: 'products',
        template: 'InvoicePaymentRegisterScreenWidget',

        /**
         * @override
         */
        init: function (options) {
            this._super.apply(this, arguments);
            this.pos.payment_register = this;
            this.invoicePaymentRegisterScreen = new PosPRScreen(null, {
                pos: this.pos,
                paymentRegister: this,
            });
        },

        /**
         * @override
         */
        renderElement: function () {
            this._super.apply(this, arguments);
            this.invoicePaymentRegisterScreen.mount(this.el.querySelector('#js_pos_payment_register_screen'));
        },

        /**
         * @override
         */
        show: function (reload) {
            this._super(); // We need to check if the user has selected a customer
            if (this.pos.get_client()) {
                this.invoicePaymentRegisterScreen.state.partner = this.pos.get_client();
            }
        },

        /**
         * @private
         */
        _go_to_back_screen: function () {
            this.gui.show_screen(this.back_screen);
        },

        /**
         * @private
         */
        _go_to_payment_list_screen: function () {
            this.gui.show_screen('invoice_payment_list_screen');
        },
    });


    const InvoicePaymentListScreenWidget = screens.ScreenWidget.extend({
        template: 'InvoicePaymentListScreenWidget',

        events: {
            'click .back': '_go_to_back_screen',
        },
 /**
         * @override
         */
        init: function (options) {
            this._super.apply(this, arguments);
            this.pos.payment_register = this;
            this.owlComponent = new InvoicePaymentListScreen(null, {
                pos: this.pos,
                paymentRegister: this,
            });
        },

        /**
         * @override
         */
        renderElement: function () {
            this._super.apply(this, arguments);
            this.owlComponent.mount(this.el.querySelector('#js_payment_list_placeholder'));
        },

        /**
         * @override
         */
        show: function (reload) {
            this._super(); // We need to check if the user has selected a customer
            // if (this.pos.get_client()) {
            this.owlComponent.state.partner = this.pos.get_client();
            this.owlComponent.updateGroupList();
            // }
        },

        /**
         * @private
         */
        _go_to_back_screen: function () {
            this.gui.show_screen('invoice_payment_register_screen');
        },
    })

    gui.define_screen({name: 'invoice_payment_register_screen', widget: InvoicePaymentRegisterScreenWidget});
    gui.define_screen({name: 'invoice_payment_list_screen', widget: InvoicePaymentListScreenWidget});

    return {
        InvoicePaymentRegisterScreenWidget,
        InvoicePaymentListScreenWidget
    };
});
