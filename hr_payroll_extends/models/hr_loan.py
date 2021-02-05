# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class HrLoan(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "hr.loan"
    _description = "Employee Loan"

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
    amount = fields.Monetary(string="Amount",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]})
    payslip_deduction = fields.Monetary(string="Payslip Deduction",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]})
    date_requested = fields.Date(string="Request Date",
        required=True,
        default=fields.Date.today(),
        readonly=True,
        states={"draft": [("readonly", False)]})
    date_disbursement = fields.Date(string="Disbursement Date",
        readonly=True,
        states={"draft": [("readonly", False)]})
    date_deduction = fields.Date(string="Deduction Start Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]})
    state = fields.Selection(string="Status",
        selection=[
            ("draft", "Draft"),
            ("open", "Open"),
            ("paid", "Paid"),
            ("cancel", "Canceled")],
        default="draft")
    payment_ids = fields.One2many(string="Payments",
        comodel_name="hr.loan.payment",
        inverse_name="loan_id",
        readonly=True)
    total_paid = fields.Monetary(string="Total Paid",
        store=True,
        compute="_compute_total_paid")

    @api.depends("payment_ids.payslip_state")
    def _compute_total_paid(self):
        for rec in self:
            total = 0
            for payment in rec.payment_ids.filtered(lambda r: r.payslip_state == "done"):
                if payment.credit_note:
                    total -= payment.amount
                else:
                    total += payment.amount
            rec.total_paid = total

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0.0:
                raise ValidationError("Amount must be greater than 0.")

    @api.constrains("payslip_deduction")
    def _check_payslip_deduction(self):
        for rec in self:
            if rec.payslip_deduction <= 0.0:
                raise ValidationError("Payslip Deduction must be greater than 0.")
            elif rec.payslip_deduction > rec.amount:
                raise ValidationError("Paylsip Deduction cannot be greater than Amount.")

    def unlink(self):
        if any(self.filtered(lambda loan: loan.state not in ("draft"))):
            raise UserError("You cannot delete a loan not in draft.")
        return super(HrLoan, self).unlink()

    def _write(self, vals):
        res = super(HrLoan, self)._write(vals)
        self.filtered(lambda loan: loan.state == "open" and loan.total_paid >= loan.amount).action_loan_paid()
        self.filtered(lambda loan: loan.state == "paid" and loan.total_paid < loan.amount).action_loan_open()
        return res

    def action_loan_open(self):
        for rec in self:
            if not rec.date_disbursement:
                raise ValidationError("You cannot confirm a loan if Disbursement Date is not set.")
        return self.write({"state": "open"})

    def action_loan_cancel(self):
        return self.write({"state": "cancel"})

    def action_loan_paid(self):
        return self.write({"state": "paid"})