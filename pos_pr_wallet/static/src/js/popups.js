odoo.define("pos_pr_wallet.payment_register.popups", function (require) {


    const PosBaseWidget = require('point_of_sale.BaseWidget');
    const PopupWidget = require('point_of_sale.popups');
    const {_t} = require("web.core");
    const gui = require('point_of_sale.gui');
    const {
        LoadWalletWithChangePopupApp,
        PayInvoiceWithWalletPopupApp,
    } = require('pos_pr_wallet.owl.components');

    const LoadWalletWithChangePopup = PopupWidget.extend({
        template: 'LoadWalletWithChange.Popup',

        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.wallets = this.pos.config.wallet_category_ids.map(wallet_id => this.call('WalletService', 'getWalletById', wallet_id));
            this.rows = [];
            this.loadWalletPopupApp = new LoadWalletWithChangePopupApp(null, {pos: this.pos});
        },

        renderElement: function () {
            this._super.apply(this, arguments);
            this.loadWalletPopupApp.mount(this.el.querySelector('.owl_wallet_load_container'));
        },
    });
    gui.define_popup({name: 'posPrWalletLoadWithChange', widget: LoadWalletWithChangePopup});

    const PayInvoiceWithWallet = PopupWidget.extend({
        template: 'PayInvoiceWithWallet.Popup',

        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.wallets = this.pos.config.wallet_category_ids.map(wallet_id => this.call('WalletService', 'getWalletById', wallet_id));
            this.rows = [];
            this.invoice = {};
            this.payInvoiceWithWalletPopupApp = new PayInvoiceWithWalletPopupApp(null, {pos: this.pos});
        },

        /**
         * @override
         */
        show: function (options) {
            if (typeof options !== 'string') {
                this.invoice = options.invoice || {}
                this.paymentRegister = options.paymentRegister || {}
                this.payInvoiceWithWalletPopupApp.paymentRegister = this.paymentRegister;
            }
            this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        renderElement: function () {
            this._super.apply(this, arguments);
            this.payInvoiceWithWalletPopupApp.mount(this.el.querySelector('.owl_wallet_payment_container'))
            this.payInvoiceWithWalletPopupApp.paymentState.invoice = this.invoice;
            // this.payInvoiceWithWalletPopupApp.onMounted(() => {
            //     console.log(...arguments);
            // });
        },


        /**
         * @override
         */
        hide: function () {
            this.payInvoiceWithWalletPopupApp.paymentState.invoice = {};
            this.payInvoiceWithWalletPopupApp.walletAmounts = {};
            this._super.apply(this, arguments);
        },

    });
    gui.define_popup({name: 'posPrWalletPayInvoice', widget: PayInvoiceWithWallet});

});