# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrPayslipDeduction(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "hr.payslip.deduction"
    _description = "Payslip Deduction"

    payslip_id = fields.Many2one(string="Payslip",
        comodel_name="hr.payslip",
        required=True,
        ondelete="cascade")
    move_line_id = fields.Many2one(string="Journal Item",
        comodel_name="account.move.line",
        required=True,
        readonly=True)
    move_id = fields.Many2one(string="Invoice",
        comodel_name="account.move",
        related="move_line_id.move_id")
    account_id = fields.Many2one(string="Account",
        comodel_name="account.account",
        related="move_line_id.account_id")
    due_date = fields.Date(string="Due Date",
        related="move_line_id.date_maturity")
    company_id = fields.Many2one(string="Company",
        comodel_name="res.company",
        related="payslip_id.company_id",
        readonly=True)
    currency_id = fields.Many2one(string="Currency",
        comodel_name="res.currency",
        related="company_id.currency_id",
        readonly=True)
    amount = fields.Monetary(string="Amount",
        required=True)