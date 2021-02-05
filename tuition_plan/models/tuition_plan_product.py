# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TuitionPlanProduct(models.Model):
    _name = "tuition.plan.product"
    _description = "Tuition Plan Product"

    plan_id = fields.Many2one(string="Tuition Plan",
        comodel_name="tuition.plan",
        required=True,
        ondelete="cascade")
    product_id = fields.Many2one(string="Product",
        comodel_name="product.product",
        required=True,
        domain="[('categ_id','child_of',parent.category_id)]",
        ondelete="cascade")
    type = fields.Selection(string="Type",
        selection=[
            ("monthly", "Monthly"),
            ("annual", "Annual")],
        required=True,
        default="annual")
    amount = fields.Float(string="Amount")
    analytic_account_id = fields.Many2one(string="Analytic Account",
        comodel_name="account.analytic.account",
        help="Analytic account to use in the invoice. If empty, the analytic account in the tution plan is used. Not used if no invoice is created")
    installment_ids = fields.Many2many(string="Installments",
        comodel_name="tuition.plan.installment",
        relation="plan_product_plan_installment_rel",
        domain="[('plan_id','=',parent.id)]",
        help="Dates to include this product on")
    installment2_ids = fields.Many2many(string="Installments2",
        comodel_name="tuition.plan.installment",
        related="installment_ids",
        help="Dates to include this product on")
    automation = fields.Selection(string="Automation",
        related="plan_id.automation")
    category_id = fields.Many2one(string="Category",
        comodel_name="product.category",
        related="product_id.categ_id",
        store=True)

    def _prepare_order_line_vals(self):
        self.ensure_one()
        return {
            "product_id": self.product_id.id,
            "price_unit": self.amount,
            "display_type": False,
        }
