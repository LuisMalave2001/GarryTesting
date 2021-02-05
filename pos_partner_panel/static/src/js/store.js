odoo.define('pos_partner_panel.owl.store', require => {
    "use strict";

    const store = new owl.Store({
        state: {
            current_client: {},
        },
        actions: {
            setPartner({state}, newPartner) {
                state.current_client = newPartner || {};
            }
        }
    });
    store.dispatch('setPartner', {});
    return store;

});