# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    price_unit_signed = fields.Float(string="Unit Price (Signed)", compute="_compute_price_unit_signed", store=True)

    @api.depends("price_unit")
    def _compute_price_unit_signed(self):
        for line in self:
            line.price_unit_signed = line.price_unit if line.move_id.type == "out_invoice" else - line.price_unit