#-*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrPayslipEmployees(models.TransientModel):
    _inherit = "hr.payslip.employees"

    def compute_sheet(self):
        salary_structure_type = self.env["hr.payslip.run"]
        if self._context.get("active_id"):
            salary_structure_type = self.env["hr.payslip.run"].browse(self.env.context.get("active_id")).type_id
        res = super(HrPayslipEmployees, self.with_context(salary_structure_type=salary_structure_type)).compute_sheet()
        payslips = self.env["hr.payslip"].search([("payslip_run_id","=",res["res_id"])])
        for payslip in payslips:
            payslip._compute_loan_and_savings_payments()
            payslip.compute_sheet()
        return res
