odoo.define("pos_wallet.load_partner_fields", function (require) {
    "use strict";

    const PosDB = require('point_of_sale.DB');
    const models = require('point_of_sale.models');
    models.load_fields('res.partner', ['json_dict_wallet_amounts', 'pos_wallet_has_invoice', 'pos_wallet_has_unpaid_invoice']);

    PosDB.include({
        add_partners: function (partners) {
            let updated_count = this._super(partners);

            _.each(partners, partner => {
                partner.json_dict_wallet_amounts = JSON.parse(partner.json_dict_wallet_amounts)
                // partner.pos_wallet_has_invoice = JSON.parse(partner.json_dict_wallet_amounts)
                // partner.pos_wallet_has_unpaid_invoice = partner.pos_wallet_has_unpaid_invoice
            })

            return updated_count;
        }
    })

});