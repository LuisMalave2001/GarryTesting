# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
import typing

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pos_session_student_wallet_load_ids = fields.One2many('pos_wallet.wallet.load', 'student_id')
    pos_session_family_wallet_load_ids = fields.One2many('pos_wallet.wallet.load', 'family_id')

    @api.depends('pos_session_wallet_load_ids', 'pos_session_student_wallet_load_ids', 'pos_session_student_wallet_load_ids')
    def _compute_pos_wallet_rels(self):
        super(ResPartner, self)._compute_pos_wallet_rels()
        for partner in self:
            pos_session_rel_wallet_load_ids = partner.pos_session_rel_wallet_load_ids

            if partner.person_type != 'student':
                pos_session_rel_wallet_load_ids = pos_session_rel_wallet_load_ids.filtered(lambda load: not load.student_id)

                if not partner.is_family:
                    pos_session_rel_wallet_load_ids = pos_session_rel_wallet_load_ids.filtered(lambda load: not load.family_id)

            partner.pos_session_rel_wallet_load_ids = pos_session_rel_wallet_load_ids + partner.pos_session_student_wallet_load_ids + partner.pos_session_family_wallet_load_ids
