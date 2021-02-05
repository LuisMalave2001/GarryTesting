#-*- coding:utf-8 -*-

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    type_id = fields.Many2one(string="Salary Structure Type",
        comodel_name="hr.payroll.structure.type")

    @api.onchange("type_id")
    def _onchange_type_id(self):
        close_date = self.type_id.default_close_date
        if close_date > 0:
            self.date_end = fields.Date.to_string(date.today().replace(day=close_date))
            self.date_start = self.date_end + relativedelta(months=-1, days=1)
    
    def unlink(self):
        for batch in self.filtered(lambda x: not x.slip_ids):
            batch.action_draft()
        return super(HrPayslipRun, self).unlink()