# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MultipleDiscounts(models.Model):
    _name = 'multiple_discounts.discount'
    _description = 'Multiple Discounts applicable to customers'

    name = fields.Char("Name", required=True)
    percent = fields.Float("Percent", digits='Multiple Discount', default=0.0, required=True)
    category_id = fields.Many2one("product.category", required=True)
    
    account_id = fields.Many2one('account.account', required=True, string='Account', index=True, ondelete="cascade", domain=[('deprecated', '=', False)])
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True)

    product_id = fields.Many2one('product.template', string='Product', required=True)

    @api.model
    def create(self, vals):
        product_id = self.env["product.template"].create({
            "name": vals["name"],
            "property_account_income_id": vals["account_id"],
            "categ_id": vals["category_id"],
            "type": "service",
            "list_price": 0.0,
            "taxes_id": False,
        })

        vals.update({
            "product_id": product_id.id
        })

        return super().create(vals)

