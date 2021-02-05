odoo.define('wallet.models', function (require) {

    const Class = require('web.Class');

    const WalletCategory = Class.extend({

        init: function (
            id,
            name,
            category,
            parent_wallet,
            parent_wallet_count,
            child_wallet_ids,
            is_default_wallet,
            credit_limit,
            company,
        ) {
            this.id = id;
            this.name = name;
            this.category = category;
            this.parent_wallet = parent_wallet;
            this.parent_wallet_count = parent_wallet_count;
            this.child_wallet_ids = child_wallet_ids;
            this.is_default_wallet = is_default_wallet;
            this.credit_limit = credit_limit;
            this.company = company;
        }
    });

    /**
     * We want a builder to improve readability
     */
    const WalletCategoryBuilder = Class.extend({

        init: function () {
            this.id = undefined;
            this.name = '';
            this.category = {};
            this.parent_wallet = {};
            this.parent_wallet_count = 0;
            this.child_wallet_ids = [];
            this.is_default_wallet = false;
            this.company = {};
        },

        setId: function (id) {
            this.id = id;
            return this;
        },

        setName: function (name) {
            this.name = name;
            return this;
        },

        setCategory: function (category) {
            this.category = category;
            return this;
        },

        setCompany: function (company) {
            this.company = company;
            return this;
        },

        setParentWallet: function (parent_wallet) {
            this.parent_wallet = parent_wallet;
            return this;
        },

        setParentWalletCount: function (parent_wallet_count) {
            this.parent_wallet_count = parent_wallet_count;
            return this;
        },

        setChildWallets: function (child_wallet_ids) {
            this.child_wallet_ids = child_wallet_ids;
            return this;
        },

        setIsDefaultWallet: function (is_default_wallet) {
            this.is_default_wallet = is_default_wallet;
            return this;
        },

        setCreditLimit: function (credit_limit) {
            this.credit_limit = credit_limit;
            return this;
        },

        build: function() {
            return new WalletCategory(
                this.id,
                this.name,
                this.category,
                this.parent_wallet,
                this.parent_wallet_count,
                this.child_wallet_ids,
                this.is_default_wallet,
                this.credit_limit,
                this.company,
            )
        }
    });

    return {
        WalletCategory: WalletCategory,
        WalletCategoryBuilder: WalletCategoryBuilder,
    };
})