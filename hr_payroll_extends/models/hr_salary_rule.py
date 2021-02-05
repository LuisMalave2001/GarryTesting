#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    is_zero = fields.Boolean(string="Hide when Zero amount",
        default=False,
        help="When checked, this rule will be hidden when the calculated amount is zero.")

    @api.onchange("is_zero")
    def _set_python_code(self):
        for r in self:
            if r.is_zero:
                r.condition_select = 'python'
                r.condition_python = r.amount_python_compute
            else:
                r.condition_select = 'none'