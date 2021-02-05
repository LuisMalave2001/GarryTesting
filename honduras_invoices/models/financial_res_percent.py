# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FinacialResponsabilityPercent(models.Model):
    _name = "honduras_invoices.financial.res.percent"
    _description = "Realted model to finance responsabilty"

    partner_id = fields.Many2one("res.partner", string="Customer", domain=[("is_family", "=", False)])
    partner_family_ids = fields.Many2many(related="partner_id.family_ids")

    family_id = fields.Many2one("res.partner", required=True, string="Family", domain=[("is_family", "=", True), ('is_company', '=', True)])
    category_id = fields.Many2one("product.category", required=True, string="Category", domain=[("parent_id", "=", False)])
    percent = fields.Integer("Percent")

    @api.onchange('family_id')
    def _get_family_domain(self):
        self.ensure_one()
        family_ids = self.partner_id.family_ids.ids
        return  {'domain':{'family_id':[('id', 'in', family_ids)]}}
