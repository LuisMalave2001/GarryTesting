#-*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrContractAdjustment(models.Model):
    _name = "hr.contract.adjustment"
    _description = "Contract Pay Adjustment"
    _order = "date desc, id"

    name = fields.Char(string="Reference",
        required=True)
    code = fields.Char(string="Code")
    contract_id = fields.Many2one(string="Contract",
        comodel_name="hr.contract",
        required=True,
        ondelete="cascade")
    type = fields.Selection(string="Type",
        required=True,
        selection=[
            ("allowance", "Allowance"),
            ("deduction", "Deduction")])
    date = fields.Date(string="Date")
    amount = fields.Float(string="Amount",
        required=True)
    is_locked = fields.Boolean(string="Locked",
        compute="_compute_is_locked")
    
    @api.model
    def create(self, vals):
        res = super(HrContractAdjustment, self).create(vals)
        if res.is_locked:
            raise ValidationError("Cannot add adjustment. A validated payslip for this contract already exists for this date.")
        return res

    def write(self, vals):
        error_msg = "Cannot edit adjustment. A validated payslip for this contract already exists for this date."
        if any(self.mapped("is_locked")):
            raise ValidationError(error_msg)
        res = super(HrContractAdjustment, self).write(vals)
        if any(self.mapped("is_locked")):
            raise ValidationError(error_msg)

    def unlink(self):
        if any(self.mapped("is_locked")):
            raise ValidationError("Cannot delete adjustment. A validated payslip for this contract already exists for this date.")
        return super(HrContractAdjustment, self).unlink()
    
    def _compute_is_locked(self):
        for adj in self:
            adj.is_locked = False
            if adj.date:
                payslip = self.env["hr.payslip"].sudo().search([
                    ("contract_id","=",adj.contract_id.id),
                    ("date_from","<=",adj.date),
                    ("date_to",">=",adj.date),
                    ("state","=","done")])
                if payslip:
                    adj.is_locked = True
