# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pos_session_wallet_load_ids = fields.One2many('pos_wallet.wallet.load', 'partner_id')
    pos_session_rel_wallet_load_ids = fields.Many2many('pos_wallet.wallet.load', store=True, compute='_compute_pos_wallet_rels')

    # It's just a prefix pos_wallet to avoid conflict with other modules
    pos_wallet_has_invoice = fields.Boolean(store=True, compute='_compute_wallet_boolean_fields', default=False)
    pos_wallet_has_unpaid_invoice = fields.Boolean(store=True, compute='_compute_wallet_boolean_fields', default=False)

    @api.depends('pos_session_wallet_load_ids')
    def _compute_pos_wallet_rels(self):
        for partner in self:
            partner.pos_session_rel_wallet_load_ids = partner.pos_session_wallet_load_ids

    @api.depends('invoice_ids')
    def _compute_wallet_boolean_fields(self):
        for partner_id in self.filtered(lambda partner: partner.invoice_ids.filtered(lambda inv: inv.state == 'posted')):
            invoices = partner_id.invoice_ids.filtered(lambda inv: inv.state == 'posted')
            partner_id.pos_wallet_has_invoice = bool(invoices)
            partner_id.pos_wallet_has_unpaid_invoice = bool(invoices.filtered(lambda inv: inv.invoice_payment_state and inv.invoice_payment_state != 'paid' or inv.amount_residual > 0))

    @api.depends('invoice_ids', 'pos_session_rel_wallet_load_ids', 'pos_order_ids')
    def _compute_json_dict_wallet_amounts(self):
        super(ResPartner, self)._compute_json_dict_wallet_amounts()

    def get_wallet_balances_dict(self, wallet_id_list: typing.List[int]) -> dict:
        wallet_balances_dict = super().get_wallet_balances_dict(wallet_id_list)

        for wallet_id, balance in wallet_balances_dict.items():
            wallet_loads = self.pos_session_rel_wallet_load_ids.filtered(
                lambda wallet_load:
                    wallet_load.pos_session_id.state != 'closed'
                    and wallet_load.wallet_category_id.id == wallet_id)

            real_final_balance = balance + sum(wallet_loads.mapped('amount'))
            wallet_balances_dict[wallet_id] = real_final_balance

        return wallet_balances_dict
