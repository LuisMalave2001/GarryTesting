odoo.define('pos_wallet.popups', function (require) {

    const PopupWidget = require('point_of_sale.popups');
    const gui = require('point_of_sale.gui');
    const {_t} = require('web.core');

    const {PosWalletLoadWalletComponent} = require('pos_wallet.owl.components');


    const LoadWalletPopup = PopupWidget.extend({
        template: 'PosWalletLoadWalletForm',

        events: _.extend({}, PopupWidget.prototype.events, {
            // 'focusout .js_wallet_amount': '_validateForm',
            'submit .js_load_wallet_popup_form': '_onSubmitLoadWalletForm',
        }),


        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.options.wallets = this.pos.config.wallet_category_ids;
            this.posWalletLoadWalletComponent = new PosWalletLoadWalletComponent(null, {walletPopup: this, pos: this.pos});
        },

        renderElement: function () {
            this._super.apply(this, arguments);

            const owlComponentToMountEl = this.el.querySelector('.js_load_wallet_owl_component');
            
            const __owl__ = this.posWalletLoadWalletComponent.__owl__;
                if (__owl__.isMounted) {
                    this.posWalletLoadWalletComponent.unmount();
                }

                if (this.pos.get_client()) {
                    if (__owl__.currentFiber) {
                        __owl__.currentFiber.cancel();
                        __owl__.currentFiber = null;
                    }
                    this.posWalletLoadWalletComponent.mount(owlComponentToMountEl);
                }
        },

        show: function () {
            this._super.apply(this, arguments);
            this.posWalletLoadWalletComponent.state.currentPartner = this.pos.get_client();

            if (this.options.wallets && this.options.wallets.length) {
                this.posWalletLoadWalletComponent.state.walletCategory = this.options.wallets[0].id;
            }
            if (this.pos.payment_methods && this.pos.payment_methods.length) {
                this.posWalletLoadWalletComponent.state.paymentMethod = this.pos.payment_methods[0].id;
            }
            this.posWalletLoadWalletComponent.state.paymentAmount = 0;
        },

        _build_load_wallet_options: function () {
            return  {
                partner_id: this.pos.get_client().id,
                wallet_category_id: parseInt(this.$el.find('.js_wallet_category').val()),
                payment_method_id: parseInt(this.$el.find('.js_payment_method').val()),
                amount: parseFloat(this.$el.find('.js_wallet_amount').val()),
            }
        },

        /**
         * @param {Event} event
         * @private
         */
        _onSubmitLoadWalletForm: function (event) {
            event.preventDefault();
            this.gui.close_popup();

            const walletLoad = this.pos.load_wallet(this._build_load_wallet_options());
            this.gui.show_screen('walletLoadReceipt', {walletLoad: walletLoad});
        }
    });
    gui.define_popup({name: 'posPrLoadWallet', widget: LoadWalletPopup});

    return {
        LoadWalletPopup,
        PosWalletLoadWalletComponent
    }
});