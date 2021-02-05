#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = "hr.contract"

    allowance_ids = fields.One2many(string="Allowances",
        comodel_name="hr.contract.adjustment",
        inverse_name="contract_id",
        domain=[("type","=","allowance"),("date","=",False)],
        copy=True)
    other_allowance_ids = fields.One2many(string="Other Allowances",
        comodel_name="hr.contract.adjustment",
        inverse_name="contract_id",
        domain=[("type","=","allowance"),("date","!=",False)],
        copy=True)
    deduction_ids = fields.One2many(string="Deductions",
        comodel_name="hr.contract.adjustment",
        inverse_name="contract_id",
        domain=[("type","=","deduction"),("date","=",False)],
        copy=True)
    other_deduction_ids = fields.One2many(string="Other Deductions",
        comodel_name="hr.contract.adjustment",
        inverse_name="contract_id",
        domain=[("type","=","deduction"),("date","!=",False)],
        copy=True)
    contribution_ids = fields.One2many(string="Contributions",
        comodel_name="hr.contract.contribution",
        inverse_name="contract_id",
        copy=True)
    
    def get_allowances_amount(self, code=False):
        self.ensure_one()
        return sum(self.allowance_ids.filtered(lambda l: l.code == code).mapped("amount"))

    def get_other_allowances_amount(self, date_from, date_to, code=False):
        self.ensure_one()
        covered_allowances = self.other_allowance_ids.filtered(
            lambda l: l.date >= date_from and l.date <= date_to and l.code == code)
        return sum(covered_allowances.mapped("amount"))
    
    def get_deductions_amount(self, code=False):
        self.ensure_one()
        return sum(self.deduction_ids.filtered(lambda l: l.code == code).mapped("amount"))

    def get_other_deductions_amount(self, date_from, date_to, code=False):
        self.ensure_one()
        covered_deductions = self.other_deduction_ids.filtered(
            lambda l: l.date >= date_from and l.date <= date_to and l.code == code)
        return sum(covered_deductions.mapped("amount"))
    
    def get_contributions_amount(self, company=False, partner_id=None, code=False, wage=False):
        self.ensure_one()
        total_amount = 0
        for contrib in self.contribution_ids.filtered(lambda l: l.code == code):
            employee_amount, company_amount = contrib._get_distributed_amount(wage=wage)
            amount = company_amount if company else employee_amount
            if not partner_id:
                total_amount += amount
            elif partner_id and partner_id == contrib.partner_id.id:
                total_amount += amount
        return total_amount