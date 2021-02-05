# -*- coding: utf-8 -*-

from odoo import models, fields, _, api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def default_settings_values(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    for company_id in env['res.company'].search([('default_wallet_category_id', '=', False)]):
        company_id.compute_new_wallet_category()

