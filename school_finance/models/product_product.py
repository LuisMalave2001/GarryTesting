from odoo import fields, models, api


class ProductProduct (models.Model):
    _inherit = 'product.product'

    categ_facts_id = fields.Char("Fact id", related="categ_id.facts_id")

class ProductTemplate (models.Model):
    _inherit = 'product.template'

    categ_facts_id = fields.Char("Fact id", related="categ_id.facts_id")
