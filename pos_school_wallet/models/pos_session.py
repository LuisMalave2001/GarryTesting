# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import fields, models, api, _, exceptions


class PosSession(models.Model):
    _inherit = "pos.session"

    def _validate_session(self):
        action = super()._validate_session()

        if self.pos_wallet_load_ids:
            self.pos_wallet_load_ids.mapped('student_id')._compute_json_dict_wallet_amounts()
            self.pos_wallet_load_ids.mapped('family_id')._compute_json_dict_wallet_amounts()

        return action

