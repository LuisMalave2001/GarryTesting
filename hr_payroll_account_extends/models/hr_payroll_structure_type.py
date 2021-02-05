#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrPayrollStructureType(models.Model):
    _inherit = "hr.payroll.structure.type"

    invoice_payment_scope = fields.Selection(string="Invoice Payment Scope",
        selection=[
            ("unpaid", "All Unpaid"),
            ("overdue", "Overdue Only"),
            ("overdue_end_of_period", "Overdue only at the end of the period")],
        default="unpaid",
        help="Which unpaid invoice amount should be considered for payslip deduction. Leave empty if you don't want to deduct invoices")