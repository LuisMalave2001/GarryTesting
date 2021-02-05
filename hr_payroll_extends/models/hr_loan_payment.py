# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrLoanPayment(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "hr.loan.payment"
    _description = "Employee Loan Payment"

    payslip_id = fields.Many2one(string="Payslip",
        comodel_name="hr.payslip",
        required=True,
        ondelete="cascade")
    loan_id = fields.Many2one(string="Loan",
        comodel_name="hr.loan",
        required=True)
    code = fields.Char(string="Code",
        related="loan_id.code")
    partner_id = fields.Many2one(string="Partner",
        related="loan_id.partner_id",
        readonly=True)
    company_id = fields.Many2one(string="Company",
        comodel_name="res.company",
        related="loan_id.company_id",
        readonly=True)
    date_paid = fields.Date(string="Date Paid",
        related="payslip_id.date_to",
        readonly=True)
    currency_id = fields.Many2one(string="Currency",
        comodel_name="res.currency",
        related="company_id.currency_id",
        readonly=True)
    amount = fields.Monetary(string="Amount",
        required=True)
    payslip_state = fields.Selection(string="Payslip State",
        related="payslip_id.state",
        readonly=True)
    credit_note = fields.Boolean(string="Credit Note",
        related="payslip_id.credit_note")