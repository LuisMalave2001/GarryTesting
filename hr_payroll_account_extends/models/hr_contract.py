#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = "hr.contract"

    emp_contribution_ids = fields.One2many(string="Employee Contributions",
        comodel_name="hr.contract.contribution",
        inverse_name="contract_id")
    comp_contribution_ids = fields.One2many(string="Company Contributions",
        comodel_name="hr.contract.contribution",
        inverse_name="contract_id")