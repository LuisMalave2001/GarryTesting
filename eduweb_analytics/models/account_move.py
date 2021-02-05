# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id_update_analytic(self):
        for line in self:
            line.analytic_account_id = line.product_id.analytic_account_id

    @api.model
    def default_get(self, fields):
        result = super(AccountMoveLine, self).default_get(fields)

        if 'analytic_account_id' in fields:
            result['analytic_account_id'] = self.product_id.analytic_account_id.id

        return result
