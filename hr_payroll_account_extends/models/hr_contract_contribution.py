#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrContractContribution(models.Model):
    _inherit = "hr.contract.contribution"

    emp_product_id = fields.Many2one(string="Emp. Product",
        comodel_name="product.product",
        required=True)
    emp_journal_id = fields.Many2one(string="Emp. Journal",
        comodel_name="account.journal",
        required=True)
    emp_debit_account_id = fields.Many2one(string="Emp. Debit Acct.",
        comodel_name="account.account")
    emp_credit_account_id = fields.Many2one(string="Emp. Credit Acct.",
        comodel_name="account.account")
    emp_analytic_account_id = fields.Many2one(string="Emp. Analytic Acct.",
        comodel_name="account.analytic.account")
    comp_product_id = fields.Many2one(string="Comp. Product",
        comodel_name="product.product",
        required=True)
    comp_journal_id = fields.Many2one(string="Comp. Journal",
        comodel_name="account.journal",
        required=True)
    comp_debit_account_id = fields.Many2one(string="Comp. Debit Acct.",
        comodel_name="account.account")
    comp_credit_account_id = fields.Many2one(string="Comp. Credit Acct.",
        comodel_name="account.account")
    comp_analytic_account_id = fields.Many2one(string="Comp. Analytic Acct.",
        comodel_name="account.analytic.account")