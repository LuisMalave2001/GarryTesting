odoo.define("pos_pr_school.load.fields", function (require) {
    const models = require('point_of_sale.models');
    models.load_fields('account.move', ['student_id', 'family_id']);
})