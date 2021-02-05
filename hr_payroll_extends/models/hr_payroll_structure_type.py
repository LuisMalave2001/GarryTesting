#-*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrPayrollStructureType(models.Model):
    _inherit = "hr.payroll.structure.type"

    default_close_date = fields.Integer(string="Default Closing Date",
        help="Last day of a payroll cut-off. If set to 0, default payslip period will be start and end of month. Must be between 0 to 27.")
    unpaid_deduction_basis = fields.Selection(string="Unpaid Deduction Basis",
        selection=[
            ("working_days", "Working Days"),
            ("natural_days", "Natural Days"),
            ("fixed_days", "Fixed Days")],
        required=True,
        help="""
            Working Days - Daily rate is based on working days set for the employee
            Natural Days - Daily rate is based on actual number of days in the period
            Fixed Days - Daily rate is based on fixed number of days
        """,
        default="working_days")
    days_in_a_month = fields.Integer(string="Days in a Month")
    
    @api.constrains("default_close_date")
    def _check_default_close_date(self):
        for struct_type in self:
            if struct_type.default_close_date < 0 or struct_type.default_close_date > 27:
                raise ValidationError("Default Closing Date should be between 0 and 27 only.")

    @api.constrains("unpaid_deduction_basis", "days_in_a_month")
    def _check_days_in_a_month(self):
        for struct_type in self:
            if struct_type.unpaid_deduction_basis == "fixed_days" and struct_type.days_in_a_month <= 0:
                raise ValidationError("Days in a month must be greater than 0.")