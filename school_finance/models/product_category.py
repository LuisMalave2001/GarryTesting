from odoo import fields, models, api


class ProductCategory (models.Model):
    _inherit = 'product.category'

    facts_id_int = fields.Integer("Fact id")
    facts_id = fields.Char("Fact id (Char)", readonly=True, compute="_compute_facts_id")

    def _compute_facts_id(self):
        for record in self:
            record.facts_id = str(record.facts_id_int)
