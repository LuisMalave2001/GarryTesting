#-*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import MissingError

class HrLoan(models.Model):
    _inherit = "hr.loan"

    product_id = fields.Many2one(string="Product",
        comodel_name="product.product",
        required=True)
    journal_id = fields.Many2one(string="Journal",
        comodel_name="account.journal",
        required=True)
    bill_analytic_account_id = fields.Many2one(string="Bill Analytic Account",
        comodel_name="account.analytic.account")
    debit_account_id = fields.Many2one(string="Debit Account",
        comodel_name="account.account")
    credit_account_id = fields.Many2one(string="Credit Account",
        comodel_name="account.account")
    analytic_account_id = fields.Many2one(string="Deduction Analytic Account",
        comodel_name="account.analytic.account")
    bill_id = fields.Many2one(string="Bill",
        comodel_name="account.move",
        readonly=True)
    bill_payment_state = fields.Selection(string="Bill Status",
        related="bill_id.invoice_payment_state",
        store=True)
    
    def action_create_bill(self):
        for loan in self:
            if loan.bill_id:
                continue
            if not loan.employee_id.address_home_id:
                raise MissingError("Private address of Employee is not set. Set the private address in the employee form.")

            move_obj = self.env["account.move"]
            move_line_obj = self.env["account.move.line"]
            created_bill = move_obj.create({
                "type": "in_invoice",
                "partner_id": loan.employee_id.address_home_id.id,
                "journal_id": loan.journal_id.id,
                "invoice_date": loan.date_disbursement,
                "date": loan.date_disbursement,
                "invoice_date_due": loan.date_disbursement,
            })
            created_bill._onchange_partner_id()
            accounts = loan.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=created_bill.fiscal_position_id)
            created_line = move_line_obj.create({
                "move_id": created_bill.id,
                "product_id": loan.product_id.id,
                "account_id": accounts["expense"].id,
                "analytic_account_id": loan.bill_analytic_account_id.id,
                "quantity": 1,
            })
            created_line._onchange_product_id()
            created_bill.write({"invoice_line_ids": [(1, created_line.id, {
                "name": created_line.name + "\n" + loan.name,
                "price_unit": loan.amount,
            })]})
            loan.bill_id = created_bill.id
