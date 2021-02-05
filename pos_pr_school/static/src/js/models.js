odoo.define('pos_pr_school.models', require => {

    const { AccountMove } = require('pos_pr.models');

    AccountMove.include({
        fields: [...AccountMove.prototype.fields, ...[
            {name: 'student_id', type: 'many2one'},
            {name: 'family_id', type: 'many2one'},
        ]]
    })

});