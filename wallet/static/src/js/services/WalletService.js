odoo.define('wallet.services.WalletService', function (require) {

    const AbstractService = require('web.AbstractService');
    const core = require('web.core');

    const rpc = require('web.rpc');
    const walletModels = require('wallet.models');

    const _t = core._t;

    return rpc.query({
        model: 'wallet.category',
        method: 'search_read',
        fields: [
            'id',
            'name',
            'category_id',
            'parent_wallet_id',
            'parent_wallet_count',
            'child_wallet_ids',
            'is_default_wallet',
            'credit_limit',
            'company_id',
        ],
        domain: []
    }).then(wallets => {
        const WalletService = AbstractService.extend({
            name: 'WalletService',

            init: function () {
                this._super.apply(this, arguments);
                this.wallets = [];
                this.wallets_by_id = {};
                this.default_wallet = {};
                this.default_wallet_by_company = {};

                _.each(wallets, walletOdoo => {
                    const wallet = new walletModels.WalletCategoryBuilder()
                        .setId(walletOdoo.id)
                        .setName(walletOdoo.name)
                        .setCategory({id: walletOdoo.category_id[0], name: walletOdoo.category_id[1]})
                        .setParentWallet({id: walletOdoo.parent_wallet_id[0], name: walletOdoo.parent_wallet_id[1]})
                        .setParentWalletCount(walletOdoo.parent_wallet_count)
                        .setChildWallets(walletOdoo.child_wallet_ids)
                        .setIsDefaultWallet(walletOdoo.is_default_wallet)
                        .setCreditLimit(walletOdoo.credit_limit)
                        .setCompany({id: walletOdoo.company_id[0], name: walletOdoo.company_id[1]})
                        .build();
                    this.wallets.push(wallet);
                    this.wallets_by_id[wallet.id] = wallet;

                    if (wallet.is_default_wallet) {
                        this.default_wallet = wallet;
                        this.default_wallet_by_company[wallet.company.id] = wallet;
                    }

                });
            },

            getDefaultWalletWithChildren: function (company_id) {
                return this._getWalletWithChildren((company_id && this.default_wallet_by_company[company_id]) || this.default_wallet);
            },

            getWallets: function () {
                return this.wallets;
            },

            getDefaultWallet: function () {
                return this.default_wallet;
            },

            getWalletById: function (walletId) {
                return this.wallets_by_id[walletId];
            },

            loadWalletWithPayment: async function (partner_id, wallet_id, amount) {
                if (wallet_id && typeof (wallet_id) === 'number' && wallet_id in this.wallets_by_id) {
                    console.log(`Added: ${partner_id}, to ${this.wallets_by_id[wallet_id].name} the amount of ${amount}`)
                } else {
                    throw Error(_.str.sprintf(_t("Wallet with id: %s not found", wallet_id)));
                }
            },

            _getWalletWithChildren: function (wallet) {
                wallet.children = [];
                _.each(wallet.child_wallet_ids, childWalletId => {
                    const walletChild = this._getWalletWithChildren(this.getWalletById(childWalletId));
                    wallet.children.push(walletChild)
                });

                return wallet;
            }
        });

        core.serviceRegistry.add('WalletService', WalletService);
        return WalletService;
    })
})