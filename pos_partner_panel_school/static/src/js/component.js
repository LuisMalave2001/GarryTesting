odoo.define('pos_partner_panel_school.owl.components', require => {
    "use strict";

    const {useState, Component, patch} = owl;
    const {useRef} = owl.hooks;
    const {PosWalletPartnerScreenComponent} = require('pos_partner_panel.owl.components');

    patch(PosWalletPartnerScreenComponent, {
        _getFilters() {
            const filter = this._super();

            filter['student'] = function (content) {
                return content.data.partner.person_type === 'student';
            }

            return filter;
        }
    });

});