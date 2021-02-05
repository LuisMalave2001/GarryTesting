# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TuitionPlanDiscount(models.Model):
    _name = "tuition.plan.discount"
    _description = "Tuition Plan Discount"
    _order = "sequence"

    sequence = fields.Integer(string="Sequence",
        default=100)
    percentage = fields.Float(string="Discount %")
    plan_id = fields.Many2one(string="Tuition Plan",
        comodel_name="tuition.plan",
        required=True,
        ondelete="cascade")
    name = fields.Char(string="Child Number",
        compute="_compute_name")
    category_id = fields.Many2one(string="Category",
        comodel_name="product.category",
        domain="[('id','child_of',parent.category_id)]",
        help="Product category to apply this discount to. If empty, then it will be applied to the total amount after applying employee discounts")
    
    def _compute_name(self):
        for discount in self:
            plan_discounts = discount.plan_id.discount_ids.filtered(lambda d: d.category_id == discount.category_id).ids
            index = (plan_discounts.index(discount.id) + 1) if discount.id in plan_discounts else -1
            name = str(index)
            if index == len(plan_discounts):
                name += " and up"
            discount.name = name