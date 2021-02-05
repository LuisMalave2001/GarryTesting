# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("active")
    def _check_used_in_discount(self):
        for product in self:
            if not product.active:
                matched = self.env["multiple_discounts.discount"].search([("product_id","=",product.id)])
                if matched:
                    raise ValidationError("Cannot archive a product that is used in a discount.")
