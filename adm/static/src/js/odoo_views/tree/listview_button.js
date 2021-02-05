odoo.define('adm.listview_button', function (require) {
    "use strict";

    var core = require('web.core');
    var ListView = require('web.ListView');
    var ListController = require("web.ListController");

    var IncludeListView = {

        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.modelName === "adm.reenrollment") {
                var summary_apply_leave_btn = this.$buttons.find('button.o_crete_leave_from_summary');
                summary_apply_leave_btn.on('click', this.proxy('crete_leave_from_summary'))
            }
        },
        crete_leave_from_summary: function () {
            var self = this;
            var action = {
//                type: "ir.actions.act_window",
//                name: "Leave",
//                res_model: "hr.leave",
//                views: [[false,'form']],
//                target: 'new',
//                views: [[false, 'form']],
//                view_type : 'form',
//                view_mode : 'form',
//                flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
            };
            return this.do_action(action);
        },

    };
    ListController.include(IncludeListView);
});