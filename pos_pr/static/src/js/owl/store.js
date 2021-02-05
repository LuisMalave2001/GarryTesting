odoo.define('pos_pr.owl.store', require => {
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

            setPartner({state}, newPartner) {
                state.current_client = newPartner || {};
            }
        }
    });
    store.on('update', null, () => console.log(store.state.current_client));
    return store;

});