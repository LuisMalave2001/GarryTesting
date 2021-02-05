# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
import typing

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pos_student_order_ids = fields.One2many('pos.order', 'student_id')
    pos_family_order_ids = fields.One2many('pos.order', 'family_id')
