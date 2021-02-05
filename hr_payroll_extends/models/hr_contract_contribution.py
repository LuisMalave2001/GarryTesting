#-*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrContractContribution(models.Model):
    _name = "hr.contract.contribution"
    _description = "Contract Pay Contribution"

    name = fields.Char(string="Reference",
        required=True)
    code = fields.Char(string="Code")
    partner_id = fields.Many2one(string="Partner",
        comodel_name="res.partner",
        required=True)
    contract_id = fields.Many2one(string="Contract",
        comodel_name="hr.contract",
        required=True,
        ondelete="cascade")
    amount = fields.Float(string="Amount",
        help="If % of Wage is checked, this is the ratio of the contribution based on the wage in the contract. Otherwise, this is a fixed amount.",
        compute="_compute_amount",
        store=True,
        readonly=False,
        default=0)
    percentage_of_wage = fields.Boolean(string="% of Wage",
        help="Check if the contribution amount is a percentage of the wage in the contract.")
    employee_percent = fields.Float(string="Emp. %")
    company_percent = fields.Float(string="Comp. %")
    employee_amount = fields.Float(string="Emp. Amount",
        compute="_compute_distributed_amount")
    company_amount = fields.Float(string="Comp. Amount",
        compute="_compute_distributed_amount")
    table_id = fields.Many2one(string="Table",
        comodel_name="hr.contribution.table")

    @api.constrains("employee_percent", "company_percent")
    def _check_percents(self):
        for contrib in self:
            if contrib.employee_percent < 0.0 or contrib.company_percent < 0.0:
                raise ValidationError("Contribution percentage must be greater than 0.")
            if (contrib.employee_percent + contrib.company_percent) != 100.0:
                raise ValidationError("Employee and Company percentage must total to 100.")
    
    @api.depends("amount", "employee_percent", "company_percent", "percentage_of_wage", "contract_id.wage")
    def _compute_distributed_amount(self):
        for contrib in self:
            employee_amount, company_amount = contrib._get_distributed_amount()
            contrib.employee_amount = employee_amount
            contrib.company_amount = company_amount
    
    def _get_distributed_amount(self, wage=False):
        self.ensure_one()
        wage = wage or self.contract_id.wage
        amount = (wage * self.amount / 100.0) if self.percentage_of_wage else self._get_amount(wage=wage)
        employee_amount = amount * self.employee_percent / 100.0
        company_amount = amount * self.company_percent / 100.0
        return employee_amount, company_amount
    
    @api.depends("contract_id.wage", "table_id", "table_id.bracket_ids.lower_limit",
                 "table_id.bracket_ids.fixed_amount", "table_id.bracket_ids.percentage_amount")
    def _compute_amount(self):
        for contrib in self:
            contrib.amount = contrib._get_amount()
    
    def _get_amount(self, wage=False):
        self.ensure_one()
        wage = wage or self.contract_id.wage
        amount = self.amount
        if self.table_id and self.table_id.bracket_ids:
            amount = 0
            for bracket in self.table_id.bracket_ids[::-1]:
                if wage > bracket.lower_limit:
                    amount = bracket.fixed_amount + \
                        bracket.percentage_amount / 100 * (wage - bracket.lower_limit)
                    break
        return amount

    @api.onchange("table_id")
    def _onchange_table_id(self):
        if self.table_id:
            self.percentage_of_wage = False