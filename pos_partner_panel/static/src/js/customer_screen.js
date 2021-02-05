odoo.define("pos_wallet.customer_screen", function (require) {
    "use strict";

    // We need wait that all the screen is loaded first.
    // Just using require is like we are depending of that module ends its work
    const screens = require('point_of_sale.screens');
    const gui = require('point_of_sale.gui');
    const core = require("web.core");
    const _t = core._t;
    const AutoCompleteInput = require('eduweb_utils.AutoCompleteInput');
    const store = require('pos_partner_panel.owl.store');
    const {PosWalletPartnerScreenComponent} = require('pos_partner_panel.owl.components');

    const ProductScreenWidget = screens.ProductScreenWidget;
    // const screenCustomerController = new CustomerController();

    const PosWalletCustomerScreenWidget = screens.ScreenWidget.extend({

        events: {
            'click .test': 'alert_test',
            'click .testServiceSend': 'testServiceSend',
            'click .js_btn_popup_wallet': 'btnLoadWalletPopup',
        },

        template: 'PosWalletCustomerScreenWidget',

        init: function (options) {
            this._super.apply(this, arguments);
            // this.pos.bind('change:selectedClient', () => {
            //     this.show();
            // });
            // this.wallets = this.call('WalletService', 'getWallets');
            //
            // this.pos.bind('change:selectedClient', () => {
            //     this.renderElement();
            // });
        },

        alert_test: function () {
            const amountToLoad = parseFloat(this.el.querySelector('#walletAmountToLoad').value);
            const partnerId = this.pos.get_client().id;
            const walletId = parseInt(this.el.querySelector('#walletCategoryIdSelect').value);
            this.call('WalletService', 'loadWalletWithPayment', partnerId, walletId, amountToLoad);
            // alert(this.$el.find("#test_input").val());
        },

        renderElement: function () {
            this._super();
            this._feed_suggestion();
        },

        //////////////////////
        //  Custom Methods  //
        //////////////////////
        _feed_suggestion: function () {
            const testSuggestions = []

            _.each(this.pos.db.partner_by_id, partner_id => {
                testSuggestions.push({
                    search: this.pos.db._partner_search_string(partner_id),
                    label: partner_id.name,
                    dataset: {
                        'id': partner_id.id,
                    },
                    onclick: event => {
                        this.pos.get_order().set_client(partner_id);
                    }
                })
            })


        },

    });
    gui.define_screen({name: 'pos_wallet_customer_screen_widget', widget: PosWalletCustomerScreenWidget});

    // Append customer screen to main screen
    ProductScreenWidget.include({
        init: function () {
            this._super.apply(this, arguments);
            this.customerScreen = new PosWalletPartnerScreenComponent(null, {pos: this.pos});
            this.appendedCustomerScreen = false;

            this.pos.bind('change:selectedClient', () => {
                store.dispatch('setPartner', this.pos.get_client());
            });
            store.dispatch('setPartner', this.pos.get_client() || {});
        },

        renderElement: function () {
            this._super.apply(this, arguments);

            const auxDiv = document.createElement('DIV');
            this.el.querySelector('.window .subwindow').insertAdjacentElement('afterend', auxDiv);
            this.customerScreen.mount(auxDiv, {'position': 'self'})
        },

    })

    return PosWalletCustomerScreenWidget;

});