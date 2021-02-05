# -*- coding: utf-8 -*-

import logging
from odoo import models

logger = logging.getLogger(__name__)


class WalletCategory(models.Model):
    _inherit = 'wallet.category'

    def get_wallet_amount(self, partner_id, wallet_category_id=False):
        wallet_amount = super(WalletCategory, self).get_wallet_amount(partner_id, wallet_category_id)

        partner_id, wallet_category_id = self._parse_get_wallet_amount_params(partner_id, wallet_category_id)

        if partner_id.person_type == 'student':
            wallet_amount -= sum(self.env['pos_pr.invoice.payment'].search([
                    ('student_id', '=', partner_id.id),
                    ('payment_method_id', '=', wallet_category_id.pos_payment_method_id.id),
                ]).filtered(lambda payment: payment.pos_session_id.state in ['opened', 'closing_control'])
                                 .mapped('display_amount'))
        elif partner_id.is_family:
            wallet_amount -= sum(self.env['pos_pr.invoice.payment'].search([
                    ('student_id', '=', False),
                    ('family_id', '=', partner_id.id),
                    ('payment_method_id', '=', wallet_category_id.pos_payment_method_id.id),
                ]).filtered(lambda payment: payment.pos_session_id.state in ['opened', 'closing_control'])
                                 .mapped('display_amount'))

        return wallet_amount
