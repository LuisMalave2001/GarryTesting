#-*- coding:utf-8 -*-

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payslip_id = fields.Many2one(string="Related Payslip",
        comodel_name="hr.payslip")