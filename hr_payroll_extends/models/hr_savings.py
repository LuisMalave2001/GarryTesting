# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class HrSavings(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "hr.savings"
    _description = "Employee Savings"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    active = fields.Boolean(string="Active",
        default=True)
    name = fields.Char(string="Name",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]})
    code = fields.Char(string="Code",
        readonly=True,
        states={"draft": [("readonly", False)]})
    company_id = fields.Many2one(string="Company",
        comodel_name="res.company",
        default=lambda self: self.env["res.company"]._company_default_get())
    employee_id = fields.Many2one(string="Employee",
        comodel_name="hr.employee",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]})
    partner_id = fields.Many2one(string="Partner",
        comodel_name="res.partner",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]})
    currency_id = fields.Many2one(string="Currency",
        comodel_name="res.currency",
        related="company_id.currency_id",
        readonly=True)
    percentage_of_wage = fields.Boolean(string="% of Wage",
        help="Check if the payslip deduction is a percentage of the wage in the contract.",
        readonly=True,
        states={"draft": [("readonly", False)]})
    payslip_deduction = fields.Monetary(string="Payslip Deduction",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="If % of Wage is checked, this is the ratio of the deduction based on the wage in the contract. Otherwise, this is a fixed amount.")
    date_deduction = fields.Date(string="Deduction Start Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]})
    state = fields.Selection(string="Status",
        selection=[
            ("draft", "Draft"),
            ("open", "Open"),
            ("cancel", "Canceled")],
        default="draft")
    payment_ids = fields.One2many(string="Payments",
        comodel_name="hr.savings.payment",
        inverse_name="savings_id",
        readonly=True)
    total_saved = fields.Monetary(string="Total Savings",
        store=True,
        compute="_compute_total_saved")
    initial_balance = fields.Monetary(string="Initial Balance",
        readonly=True,
        states={"draft": [("readonly", False)]})

    @api.depends("payment_ids.payslip_state", "initial_balance")
    def _compute_total_saved(self):
        for rec in self:
            total = 0
            for payment in rec.payment_ids.filtered(lambda r: r.payslip_state == "done"):
                if payment.credit_note:
                    total -= payment.amount
                else:
                    total += payment.amount
            rec.total_saved = total + rec.initial_balance

    @api.constrains("payslip_deduction")
    def _check_payslip_deduction(self):
        for rec in self:
            if rec.payslip_deduction <= 0.0:
                raise ValidationError("Payslip Deduction must be greater than 0.")
    
    @api.constrains("initial_balance")
    def _check_initial_balance(self):
        for rec in self:
            if rec.initial_balance < 0.0:
                raise ValidationError("Initial Balance must be greater than or equal to 0.")

    def unlink(self):
        if any(self.filtered(lambda s: s.state not in ("draft"))):
            raise UserError("You cannot delete a savings not in draft.")
        return super(HrSavings, self).unlink()

    def action_savings_open(self):
        return self.write({"state": "open"})

    def action_savings_cancel(self):
        return self.write({"state": "cancel"})

    def action_savings_paid(self):
        return self.write({"state": "paid"})