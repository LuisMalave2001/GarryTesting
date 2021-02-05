odoo.define('pos_wallet.pos_wallet_methods', function (require) {

    const models = require("point_of_sale.models");
    const rpc = require('web.rpc');

    const core = require("web.core");
    const _t = core._t;
    const store = require('pos_wallet.owl.store');

    const PosModelSuper = models.PosModel;

    models.load_fields('pos.session', ['pos_wallet_load_ids']);
    models.load_fields('res.company', ['city', 'street', 'parent_id']);

    models.PosModel = models.PosModel.extend({
        initialize: function () {
            PosModelSuper.prototype.initialize.apply(this, arguments);
        },
        /**
         *
         * @param {Object} options A few options...
         * @param {Number} options.partner_id
         * @param {Number} options.wallet_category_id
         * @param {Number} options.payment_method_id
         * @param {Number} options.amount
         */

        load_wallet: function (options) {
            const walletLoadParams = this._build_pos_wallet_wallet_load_params(options);

            // If we update them later, we can duplicate some values
            this.add_wallet_loads_amounts([walletLoadParams]);

            let walletCacheParams = this.db.load('pending_wallets_load', []);
            walletCacheParams.push(walletLoadParams);
            this.db.save('pending_wallets_load', walletCacheParams);
            this.synch_wallet_transactions().then(a => console.log('Made perfectly'))

            return walletLoadParams;
        },


        /**
         *
         * @param {Object} params A few options...
         * @param {Number} params.partner_id
         * @param {Number} params.wallet_category_id
         * @param {Number} params.payment_method_id
         * @param {Number} params.amount
         */
        _build_pos_wallet_wallet_load_params: function (params) {
            return {
                "name": this.generateNextPaymentNumber(),
                "amount": params.amount,
                "date": moment().format('YYYY-MM-DD HH:mm:ss'),

                "partner_id": params.partner_id,
                "payment_method_id": params.payment_method_id,
                "wallet_category_id": params.wallet_category_id,

                "pos_session_id": this.pos_session.id,
            };
        },

        synch_wallet_transactions: function () {
            const walletLoadParameters = this.db.load('pending_wallets_load', []);
            return rpc.query({
                model: "pos_wallet.wallet.load",
                method: "create",
                args: [walletLoadParameters]
            }, {}).then(data => {
                this.db.save('pending_wallets_load', []);
            })
        },

        /**
         * This gets a object with the form:
         * {
         *     partner_id: <wallet_amount>, ...
         * }
         * It updates the current wallet for the partners
         * @param {Object} walletLoadsList
         */
        add_wallet_loads_amounts: function (walletLoadsList) {
            if (walletLoadsList) {
                // We just simply check for partner ids
                const walletLoadsByPartnerId = _.groupBy(walletLoadsList, walletLoad => walletLoad.partner_id);
                _.each(walletLoadsByPartnerId, (walletLoads, partnerId) => {
                    const partner = this.db.partner_by_id[partnerId];
                    const walletLoadsAmounts = _.chain(walletLoads).groupBy("wallet_category_id").mapObject(walletLoad => _.reduce(walletLoad, (memo, walletLoad) => memo + parseFloat(walletLoad.amount), 0)).value();
                    const partnerCurrentWalletAmounts = partner.json_dict_wallet_amounts;

                    _.each(walletLoadsAmounts, (amount, walletId) => {
                        partner.json_dict_wallet_amounts[walletId] = (partner.json_dict_wallet_amounts[walletId] || 0) + amount;
                        store.dispatch('addWalletAmount', walletId, amount);
                    });
                     // partner.json_dict_wallet_amounts = _.mapObject(partnerCurrentWalletAmounts, (amount, walletId) => _.has(walletLoadsAmounts, walletId) ? amount + walletLoadsAmounts[walletId] : amount);
                });
            }
        },


        /**
         * Get the tCurrent number in the wallet load
         * @param {Boolean} reset Reset the wallet load
         */
        getCurrentWalletLoadSequenceNumber: function (reset) {
            reset = !!reset;
            let walletLoadNumber = parseInt(this.db.load('wallet_load_number', 0));
            if (!walletLoadNumber || reset) {
                walletLoadNumber = this.pos_session.pos_wallet_load_ids.length;
            }
            this.db.save('wallet_load_number', walletLoadNumber);
            return walletLoadNumber;
        },

        /**
         * Get the next number in the wallet load
         * @param {Boolean} [reset] Reset the wallet load
         */
        getNextWalletLoadSequenceNumber: function (reset) {
            reset = !!reset;
            const nextNumber = this.getCurrentWalletLoadSequenceNumber(reset) + 1;
            this.db.save('wallet_load_number', nextNumber);
            return nextNumber;
        },

        generateNextPaymentNumber: function () {
            const nextNumber = this.getNextWalletLoadSequenceNumber();
            return 'POS-WL/'
                + this._zero_pad(this.pos_session.id, 5) + '-'
                + this._zero_pad(this.pos_session.login_number, 3) + '/'
                + this._zero_pad(nextNumber, 5);
        },

        _zero_pad: function (num, size) {
            let s = "" + num;
            while (s.length < size) {
                s = "0" + s;
            }
            return s;
        },

        /**
         * Get the company with a specific format
         */
        getFormattedCompanyAddress: function () {

            let formattedCompanyAddress = "";
            if (this.company.country) {
                formattedCompanyAddress += this.company.country.name + ', ';
            }
            if (this.company.state_id) {
                formattedCompanyAddress += this.company.state_id[1] + ', ';
            }
            if (this.company.city) {
                formattedCompanyAddress += this.company.city + ', ';
            }
            if (this.company.street) {
                formattedCompanyAddress += this.company.street;
            }
            formattedCompanyAddress = formattedCompanyAddress.trim().replace('/,$/', '');
            return formattedCompanyAddress;
        }
    })

});