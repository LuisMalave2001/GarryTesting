odoo.define('pos_partner_panel_pos_pr_school.owl.components', require => {
    "use strict";

    const {patch} = owl;
    const {PosWalletPartnerScreenComponent} = require('pos_partner_panel.owl.components');

    require('pos_partner_panel_pos_pr.owl.components');

    patch(PosWalletPartnerScreenComponent, {
        /**
         * @private
         */
        _getFilterPartnerDueInvoices(partner) {
            const invoiceList = this._super(...arguments);

            const schoolInvoiceList = _.filter(window.posmodel.db.due_invoices, invoice =>
                invoice.amount_residual > 0
                && (
                    (invoice.student_id && invoice.student_id.id === partner.id)
                    || (invoice.family_id && invoice.family_id.id === partner.id)
                )
            )

            invoiceList.push(...schoolInvoiceList);

            return invoiceList;
        }
    });

});