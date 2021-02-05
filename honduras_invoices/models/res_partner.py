#-*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import AccessError, UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    no_constant_registro_exonerado = fields.Char("No. CONSTAN. REGISTRO EXONERADO")

