# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    wallet_category_id = fields.Many2one('wallet.category')
    is_wallet_payment_method = fields.Boolean()


class WalletCategory(models.Model):
    _inherit = 'wallet.category'

    pos_payment_method_id = fields.Many2one('pos.payment.method', store=True, compute='_compute_pos_payment_method_id')

    @api.depends('name', 'account_id', 'company_id')
    def _compute_pos_payment_method_id(self):
        for wallet_category_id in self:
            receivable_account_id = wallet_category_id.account_id or wallet_category_id.company_id.account_default_pos_receivable_account_id
            if receivable_account_id:
                if not wallet_category_id.pos_payment_method_id:
                    wallet_category_id.pos_payment_method_id = self.env['pos.payment.method'].create({
                        'name': wallet_category_id.name,
                        'receivable_account_id': receivable_account_id.id,
                        'company_id': wallet_category_id.company_id.id,

                        'is_cash_count': False,
                        'wallet_category_id': wallet_category_id.id,
                        'is_wallet_payment_method': True,
                        'split_transactions': True,
                        })
                else:
                    wallet_category_id.pos_payment_method_id.update({
                        'name': wallet_category_id.name,
                        'receivable_account_id': receivable_account_id.id,
                        'company_id': wallet_category_id.company_id.id,
                        })

    def get_wallet_amount(self, partner_id, wallet_category_id=False):
        wallet_amount = super(WalletCategory, self).get_wallet_amount(partner_id, wallet_category_id)

        partner_id, wallet_category_id = self._parse_get_wallet_amount_params(partner_id, wallet_category_id)

        if wallet_category_id:
            wallet_amount -= sum(self.env['pos.payment'].search([('payment_method_id', '=', wallet_category_id.pos_payment_method_id.id), ('partner_id', '=', partner_id.id)]).mapped('amount'))

        return wallet_amount
