# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = "product.category"

    wallet_ok = fields.Boolean("For wallet use")

    external_relation_id = fields.Char(help="This is only for migration reason")
    parent_count = fields.Integer("How many category parent it has", store=True, compute="get_parent_count")

    @api.depends("parent_id")
    def get_parent_count(self):
        for record in self:
            count = 0
            parent_id = record.parent_id
            while parent_id:
                count += 1
                parent_id = parent_id.parent_id
            record.parent_count = count
