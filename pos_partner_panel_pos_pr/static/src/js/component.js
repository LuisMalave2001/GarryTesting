odoo.define('pos_partner_panel_pos_pr.owl.components', require => {
    "use strict";

    const {patch} = owl;
    const {PosWalletPartnerScreenComponent} = require('pos_partner_panel.owl.components');

    patch(PosWalletPartnerScreenComponent, {
        /**
         * @private
         */
        _getFilterPartnerDueInvoices(partner) {
            return _.filter(window.posmodel.db.due_invoices, invoice =>
                invoice.amount_residual > 0
                &&
                invoice.partner_id.id === partner.id
            )
        },

        _getFilters() {
            const filter = this._super();

            filter['has_unpaid_invoices'] = (content) => {
                const partner = content.data.partner;
                const due_invoices = this._getFilterPartnerDueInvoices(partner);
                return due_invoices.length;
            };

            return filter;
        }
    });

});