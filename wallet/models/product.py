# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    wallet_ok = fields.Boolean("For wallet use")


class ProductProduct(models.Model):
    _inherit = "product.product"
    _table = "product_product"

    wallet_ok = fields.Boolean("For wallet use")

