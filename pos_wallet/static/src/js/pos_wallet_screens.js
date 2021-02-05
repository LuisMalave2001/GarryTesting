odoo.define('pos_wallet.screens', require => {
    "use strict";

    // Imports
    const PosBaseWidget = require('point_of_sale.BaseWidget');
    const {ProductScreenWidget, ProductListWidget, PaymentScreenWidget} = require('point_of_sale.screens');
    const {PosWalletPaymentScreenComponent} = require('pos_wallet.owl.components');
    const {_t} = require("web.core");

    ////////////////////////
    // Load Wallet Screen //
    ////////////////////////

    const LoadWalletPadWidget = PosBaseWidget.extend({
        template: 'LoadWalletPadWidget',

        events: {
            'click button.o_pos_wallet_load_button': 'btnLoadWalletPopup'
        },

        btnLoadWalletPopup: function () {

            const walletList = this.pos.config.wallet_category_ids.map(wallet_id => this.pos.chrome.call('WalletService', 'getWalletById', wallet_id));

            this.gui.show_popup('posPrLoadWallet', {
                title: _t('Load wallet'),
                wallets: walletList,
                body: _t('Load Wallet!'),
            });
        },

        start: function () {
            this._super(...arguments);
            this.pos.bind('change:selectedClient', this.toggleVisibility, this);
            this.toggleVisibility();
        },
        toggleVisibility: function () {
            if (this.$el) {
                this.$el.toggleClass('oe_hidden', !this.pos.get_client());
            }
        }
    });

    ProductScreenWidget.include({
        start: function () {
            this._super.apply(this, arguments);

            this.selectAnalyticWidget = new LoadWalletPadWidget(this, {});

            if ((this.pos.db.wallet_payment_methods || []).length) {
                this.selectAnalyticWidget.replace(this.$('.placeholder-LoadWalletWidget'));
            }
        }

    });

    ////////////////////
    // Payment Screen //
    ////////////////////

    // Append customer screen to main screen
    ProductListWidget.include({
        init: function () {
            this._super.apply(this, arguments);
            this.posWalletPaymentScreen = new PosWalletPaymentScreenComponent(null, {
                pos: this.pos,
            });
        },

        renderElement: function () {
            this._super.apply(this, arguments);
            this.renderPosWalletPaymentScreen();
        },

        show: function () {
            this._super.apply(this, arguments);
            this.renderPosWalletPaymentScreen();
        },

        renderPosWalletPaymentScreen: function () {
            if (this.posWalletPaymentScreen && (this.pos.db.wallet_payment_methods || []).length) {
                const __owl__ = this.posWalletPaymentScreen.__owl__;
                if (__owl__.isMounted) {
                    this.posWalletPaymentScreen.unmount();
                }

                if (this.pos.get_client()) {
                    if (__owl__.currentFiber && !__owl__.currentFiber.isCompleted) {
                        __owl__.currentFiber.cancel();
                        __owl__.currentFiber = null;
                    }
                    this.posWalletPaymentScreen.trigger('show', false);
                    this.posWalletPaymentScreen.mount(this.el);
                }
            }
        }
    })

    PaymentScreenWidget.include({
        payment_input: function () {
            const paymentline = this.pos.get_order().selected_paymentline;
            if (paymentline.payment_method.wallet_category_id) {
                return;
            }
            this._super.apply(this, arguments);
        }
    })

    return {
        LoadWalletPadWidget,
    }

});