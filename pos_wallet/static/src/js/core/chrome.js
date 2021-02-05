odoo.define('pos_wallet.core.chrome', function (require) {
    const core = require('web.core');
    const chrome = require('point_of_sale.chrome');
    const _lt = core._lt;

    const StatusSynchWalletTransaction = chrome.StatusWidget.extend({
        // status: ['connected','connecting','disconnected','warning','error']
        template: 'StatusSynchWalletTransaction',

        event: _.extend({}, chrome.StatusWidget.event, {
            'click': 'sync_wallet_transactions',
        }),

        renderElement: function () {
            this._super.apply(this, arguments);
            const pendingWalletLoads = this.pos.db.load('pending_wallets_load', []);
            const pendingWalletPayments = this.pos.db.load('pending_wallets_payments', []);

            const pendingWalletLoadsCount = pendingWalletLoads.length + pendingWalletPayments.length;
            const pendingWalletPaymentsCount = pendingWalletLoads.length + pendingWalletPayments.length;

            if (pendingWalletPaymentsCount + pendingWalletLoadsCount > 0) {
                this.set_status('warning', pendingWalletPaymentsCount);
                this.set_payment_status('done');
            }
        },

        start: function () {
            const self = this;
            this._super.apply(this, arguments);
            this.pos.bind('wallet_transactions:synch', function (synch) {
                self.set_status(synch.state, synch.pending);
            });

            this.$el.on('click', this.synch_wallet_transactions.bind(this));
        },

        /**
         * Sych point of sale invoice payments with server
         */
        synch_wallet_transactions: function () {
            this.pos.synch_wallet_transactions();
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
                    self.widgets.splice(index, 0, self.sync_wallet_transactions);
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
        sync_wallet_transactions: {
            'name': 'sync_wallet_transactions',
            'widget': StatusSynchWalletTransaction,
            'append': '.pos-rightheader',
        },
    });

    return {
        StatusSynchWalletTransaction
    };

});
