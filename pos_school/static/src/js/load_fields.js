odoo.define('pos_school.load_fields', require => {
    "use strict";

    const models = require('point_of_sale.models');
    models.load_fields('res.partner', ['person_type', 'family_ids', 'member_ids', 'student_invoice_address_ids']);
});