odoo.define("pos_wallet.load_wallet_category", function (require) {

    const models = require("point_of_sale.models")
    const PosDB = require("point_of_sale.DB")

    models.load_fields('pos.payment.method', ['wallet_category_id'])

    PosDB.include({
        init: function (options) {
            this._super(options);
            this.wallet_payment_methods = [];
            this.payment_method_by_wallet_id = {};
        },

        add_wallet_payment_methods: function (payment_methods) {
            this.wallet_payment_methods = payment_methods;
            _.each(payment_methods, (payment_method) => {
                // If you are asking why payment_method.wallet_category_id[0] well...
                // That because that load_models below makes a RPC call to odoo and then we receive an array of array...
                // Thanks ODOO!
                // Example [[0, 'Wallet 1'],[1, 'Wallet 2'],[2, 'Wallet 3'],[3, 'Wallet 4'],]
                // The first element is the ID so payment_method.wallet_category_id[0] is the id of the wallet category
                // Att: Somebody that really hates this way to work in Odoo... You know if you would just use a
                // JSON Format we could make something like payment_method.wallet_category_id.id
                // I have dreams...
                this.payment_method_by_wallet_id[payment_method.wallet_category_id[0]] = payment_method;
            });
        }
    });

    // Load wallets payment methods
    models.load_models([
        {
            model: 'pos.payment.method',
            fields: ['name', 'wallet_category_id'],


            domain: function (self, tmp) {
                return [
                    ['wallet_category_id', '!=', false],
                ];
            },
            loaded: function (self, payment_methods) {
                self.db.add_wallet_payment_methods(payment_methods);
                _.each(payment_methods, (payment_method) => {
                    self.payment_methods_by_id[payment_method.id] = payment_method;
                });
            }
        }
    ]);


})