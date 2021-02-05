from odoo import fields, models, api


class ProductProduct (models.Model):
    _inherit = 'account.payment'

    res_id = fields.Char()
