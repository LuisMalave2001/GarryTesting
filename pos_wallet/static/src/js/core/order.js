odoo.define('pos_wallet.core.order', function (require) {

    const models = require('point_of_sale.models');
    const store = require('pos_wallet.owl.store');

    const PosModelOrder = models.Order;

    models.Order = models.Order.extend({
        initialize: function () {
            PosModelOrder.prototype.initialize.apply(this, arguments);
            this.bind('change:client', this.updateWalletClientStoreAmounts, this);
            this.bind('change:client', this.updateWalletCustomerScreenWidget, this);

            if (this.get_client()) {
                this.updateWalletClientStoreAmounts();
                this.updateWalletCustomerScreenWidget();
            }

            this.wallet_payments = [];
        },

        updateWalletClientStoreAmounts: function () {
            if (this.get_client()) {
                const json_dict_wallet_amounts = this.get_client().json_dict_wallet_amounts;
                store.dispatch('updateWalletAmount', json_dict_wallet_amounts);
            }
        },

        updateWalletCustomerScreenWidget: function () {
            store.dispatch('setPartner', this.get_client() || {});
        },

        set_wallet_payments: function (wallet_payments) {
            this.set('wallet_payments', wallet_payments);
        },

        get_wallet_payments_total: function () {
            const wallet_payments = this.get('wallet_payments', {});
            const wallet_payment_total = _.reduce(wallet_payments, ((memo, val) => memo + val), 0);
            return wallet_payment_total;
        }
    });

});
