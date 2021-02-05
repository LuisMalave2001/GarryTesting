# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('invoice_ids', 'pos_session_rel_wallet_load_ids',
                 'pos_student_invoice_payment_ids',
                 'pos_family_invoice_payment_ids',
                 'pos_order_ids',
                 'pos_student_order_ids',
                 'pos_family_order_ids')
    def _compute_json_dict_wallet_amounts(self):
        super(ResPartner, self)._compute_json_dict_wallet_amounts()
