# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


class WalletCategory(models.Model):
    _inherit = 'wallet.category'

    def get_wallet_amount(self, partner_id, wallet_category_id=False):
        wallet_amount = super(WalletCategory, self).get_wallet_amount(partner_id, wallet_category_id)

        partner_id, wallet_category_id = self._parse_get_wallet_amount_params(partner_id, wallet_category_id)

        if wallet_category_id:
            wallet_amount -= sum(self.env['pos_pr.invoice.payment'].search([
                ('payment_method_id', '=', wallet_category_id.pos_payment_method_id.id),
                ('partner_id', '=', partner_id.id)
                ]).mapped('payment_amount'))

        return wallet_amount
