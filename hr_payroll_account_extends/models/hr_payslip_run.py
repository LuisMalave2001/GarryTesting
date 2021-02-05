#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    bill_date = fields.Date(string="Bill Date",
        required=True)