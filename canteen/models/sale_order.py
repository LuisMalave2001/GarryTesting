# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_canteen_order = fields.Boolean(string="Is Canteen Order")
    canteen_order_date = fields.Date(string="Canteen Order Date")
