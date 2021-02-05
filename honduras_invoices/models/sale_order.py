# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    hide_line_price = fields.Boolean(string="Hide Line Price in Print")

    def _create_invoices(self, grouped=False, final=False):
        return super(SaleOrder, self)._create_invoices(grouped=True, final=final)