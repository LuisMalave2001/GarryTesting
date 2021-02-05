odoo.define('pos_analytics.load_data', require => {


    const models = require("point_of_sale.models")
    const PosDB = require("point_of_sale.DB")

    //////////////////////
    //      FIELDS      //
    //////////////////////
    models.load_fields('product.product', ['analytic_account_id'])

    //////////////////////
    //      MODELS      //
    //////////////////////

    // Analyitic Accounts
    models.load_models([
        {
            model: 'account.analytic.account',
            fields: ['name'],

            loaded: function (self, analytic_accounts) {
                self.db.add_analytic_accounts(analytic_accounts);
            }
        }
    ]);

    PosDB.include({
        init: function (options) {
            this._super(options);
            this.analytic_accounts = [];
            this.analytic_account_by_id = {};
        },

        add_analytic_accounts: function (analytic_accounts) {
            this.analytic_accounts = analytic_accounts;
             _.each(analytic_accounts, analytic_account => {
                this.analytic_account_by_id[analytic_account.id] = analytic_account;
            });
        }
    });
});