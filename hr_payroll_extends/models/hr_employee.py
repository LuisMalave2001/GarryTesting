# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    loan_ids = fields.One2many(string="Loans",
        comodel_name="hr.loan",
        inverse_name="employee_id",
        groups="hr_payroll.group_hr_payroll_user")
    loan_count = fields.Integer(string="Loan Count",
        compute="_compute_loan_count",
        groups="hr_payroll.group_hr_payroll_user")
    savings_ids = fields.One2many(string="Savings",
        comodel_name="hr.savings",
        inverse_name="employee_id",
        groups="hr_payroll.group_hr_payroll_user")
    savings_count = fields.Integer(string="Savings Count",
        compute="_compute_savings_count",
        groups="hr_payroll.group_hr_payroll_user")

    def _compute_loan_count(self):
        for employee in self:
            employee.loan_count = len(employee.loan_ids)
    
    def _compute_savings_count(self):
        for employee in self:
            employee.savings_count = len(employee.savings_ids)
    
    def _get_contracts(self, date_from, date_to, states=["open"], kanban_state=False):
        res = super(HrEmployee, self)._get_contracts(date_from, date_to, states=states, kanban_state=kanban_state)
        if self._context.get("salary_structure_type"):
            contracts = self.env["hr.contract"]
            for contract in res:
                if contract.structure_type_id == self._context["salary_structure_type"]:
                    contracts |= contract
            res = contracts
        if not res:
            raise ValidationError("No contracts matched for given Salary Structure Type!")
        return res