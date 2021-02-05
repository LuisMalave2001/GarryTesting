odoo.define('pos_wallet.owl.store', require => {
    "use strict";
    // store.on('update', null, () => console.log(store.state.client_wallet_balances));
    const store = new owl.Store({
        state: {
            client_wallet_balances: {},
            current_client: {},
        },
        actions: {
            updateWalletAmount({state}, walletValues) {
                _.each(walletValues, (walletAmount, walletId) => {
                    state.client_wallet_balances[parseInt(walletId)] = walletAmount;
                })
            },

            /**
             *
             * @param state
             * @param {Number} walletId
             * @param {Number} walletValues
             */
            addWalletAmount({state}, walletId, walletValues) {
                state.client_wallet_balances[walletId] = (state.client_wallet_balances[walletId] || 0) + (walletValues || 0);
                state.current_client.json_dict_wallet_amounts[walletId] = (state.current_client.json_dict_wallet_amounts[walletId] || 0) + (walletValues || 0);
            },

            /**
             *
             * @param state
             * @param {Number} walletId
             * @param {Number} walletValues
             */
            substractWalletAmount({state}, walletId, walletValues) {
                state.client_wallet_balances[walletId] = (state.client_wallet_balances[walletId] || 0) - (walletValues || 0)
                state.current_client.json_dict_wallet_amounts[walletId] = (state.current_client.json_dict_wallet_amounts[walletId] || 0) - (walletValues || 0)
            },

            setPartner({state}, newPartner) {
                state.current_client = newPartner || {};
            }
        }
    });
    store.on('update', null, () => console.log(store.state.current_client));
    return store;

});