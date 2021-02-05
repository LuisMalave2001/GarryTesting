# -*- coding: utf-8 -*-

from odoo import models, fields


class PosConfig(models.Model):
    """ Adds pos_pr_discount """
    _inherit = "pos.payment.method"

    # The only porpuse of this fields is to make a difference between normal payment methods and
    # built-in discount payment method
    is_pos_pr_discount = fields.Boolean(default=False)

