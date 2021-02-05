# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PosConfig(models.Model):

    _inherit = 'pos.config'

    wallet_category_ids = fields.Many2many('wallet.category', string='Wallet categories')
