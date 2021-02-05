# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class OrderLine(models.Model):
    _inherit = 'product.template'

    analytic_account_id = fields.Many2one('account.analytic.account')
