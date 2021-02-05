odoo.define('pos_wallet.reports.widgets', function (require) {
    'use strict';

    const BaseWidget = require('point_of_sale.BaseWidget');
    const core = require('web.core');
    const gui = require('point_of_sale.gui');

    const QWeb = core.qweb;
    const _t = core._t;

    const LoadWalletReceiptDocument = BaseWidget.extend({
        template: 'LoadWalletReport.Receipt.Document',
        //
        /**
         * This will be used to render payments receipts in POS.
         * @param {Object} parent The current parent
         * @param {Object} options Widget's options
         * @param {Object} options.wallet_load Wallet load to render
         * @param {Boolean=false} options.copy The customer to rendered
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);

            // Attributes by options
            this.wallet_load = options.wallet_load || {};
            this.wallet = this.call('WalletService', 'getWalletById', this.wallet_load.wallet_category_id)
            this.payment_method = this.pos.payment_methods_by_id[this.wallet_load.payment_method_id]
            this.partner = this.pos.db.partner_by_id[this.wallet_load.partner_id]
            this.copy = !!options.copy;

            // Default attributes
            this.company = this.pos.company;
        },
    });

    return {
        LoadWalletReceiptDocument,
    };

});
