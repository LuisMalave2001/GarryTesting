# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import fields, models, api, _, exceptions


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_payment_method_cash = fields.Boolean()
    pos_wallet_category_id = fields.Many2one('wallet.category')
