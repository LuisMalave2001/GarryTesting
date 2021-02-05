# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, MissingError

class ProductCategory(models.Model):
    _inherit = "product.category"

    exclude_from_config_check = fields.Boolean(string="Exclude from Config Check")