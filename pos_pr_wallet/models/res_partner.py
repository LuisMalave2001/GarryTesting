# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pos_pr_session_wallet_payment_ids = fields.One2many('pos_pr.invoice.payment', 'partner_id')
    pos_pr_session_wallet_surcharge_ids = fields.One2many('pos_pr.invoice.surcharge', 'partner_id')

    pos_pr_session_rel_wallet_payment_ids = fields.One2many('pos_pr.invoice.payment', 'partner_id')
    pos_pr_session_rel_wallet_surcharge_ids = fields.One2many('pos_pr.invoice.surcharge', 'partner_id')

    @api.depends('pos_pr_session_wallet_payment_ids', 'pos_pr_session_wallet_surcharge_ids')
    def _compute_pos_pr_wallet_rels(self):
        for partner in self:
            partner.pos_pr_session_rel_wallet_payment_ids = partner.pos_pr_session_wallet_payment_ids
            partner.pos_pr_session_rel_wallet_surcharge_ids = partner.pos_pr_session_wallet_surcharge_ids

    @api.depends('invoice_ids', 'pos_session_rel_wallet_load_ids', 'pos_pr_session_rel_wallet_payment_ids', 'pos_pr_session_rel_wallet_surcharge_ids', 'pos_order_ids')
    def _compute_json_dict_wallet_amounts(self):
        super(ResPartner, self)._compute_json_dict_wallet_amounts()

    def get_wallet_balances_dict(self, wallet_id_list: typing.List[int]) -> dict:
        wallet_balances_dict = super().get_wallet_balances_dict(wallet_id_list)

        # for wallet_id, balance in wallet_balances_dict.items():
        #     wallet_payments = \
        #         self.pos_pr_session_rel_wallet_payment_ids.filtered(
        #             lambda payment:
        #                 payment.payment_method_id.is_wallet_payment_method
        #                 and payment.pos_session_id.state != 'closed'
        #                 and payment.payment_method_id.wallet_category_id.id == wallet_id)
        #
        #     # wallet_surcharges = \
        #     #     self.pos_pr_session_rel_wallet_surcharge_ids.filtered(
        #     #     lambda surcharge:
        #     #     surcharge.payment_method_id.is_wallet_payment_method
        #     #     and surcharge.pos_session_id.state != 'closed'
        #     #     and surcharge.payment_method_id.id == wallet_id)
        #
        #     real_final_balance = balance - sum(wallet_payments.mapped('payment_amount'))
        #     wallet_balances_dict[wallet_id] = real_final_balance

        return wallet_balances_dict
