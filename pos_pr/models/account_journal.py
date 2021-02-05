# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    """ Setting for surcharge """
    _inherit = "account.journal"

    def _get_defualt_surcharge_product_id(self):
        product_id = int(self.env["ir.config_parameter"].get_param('pos_pr.surcharge_product_id'))

        return self.env["product.product"].browse([product_id])

    surcharge_product_id = fields.Many2one("product.product",
                                           string="Surcharge Product",
                                           default=_get_defualt_surcharge_product_id,)

    surcharge_amount = fields.Monetary(default=lambda journal: journal.env["ir.config_parameter"]
                                            .get_param('pos_pr.surcharge_default_amount'))
