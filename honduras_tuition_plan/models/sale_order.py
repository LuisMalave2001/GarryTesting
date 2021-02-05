# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        if self._context.get("override_sale_order_name"):
            vals["name"] = self._context.get("override_sale_order_name")
        return super(SaleOrder, self).create(vals)