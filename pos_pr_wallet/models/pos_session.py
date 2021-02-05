# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import fields, models, api, _


class PosSession(models.Model):
    _inherit = "pos.session"

    def _validate_session(self):
        action = super()._validate_session()
        if self.invoice_payment_ids:
            self.invoice_payment_ids.mapped('partner_id')._compute_json_dict_wallet_amounts()
        return action