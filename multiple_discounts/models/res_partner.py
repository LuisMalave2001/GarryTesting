# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    discount_ids = fields.Many2many("multiple_discounts.discount", string="Multiple discounts")
