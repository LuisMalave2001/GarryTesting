# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    default_wallet_account_id = fields.Many2one("account.account", string='Default wallet account')
    default_wallet_credit_limit = fields.Float(string='Wallet credit limit')

    default_wallet_category_id = fields.Many2one('wallet.category')

    def compute_new_wallet_category(self):
        """ Assign a new created wallet category for the companies """
        for company_id in self:
            default_wallet_category_id = self.create_new_wallet_category()
            default_wallet_category_id.company_id = company_id
            company_id.default_wallet_category_id = default_wallet_category_id

    @api.model
    def create_new_wallet_category(self):
        """ Creates and assign a new wallet category for the companies """
        wallet_category_vals = self._build_new_wallet_category_vals()
        return self.env['wallet.category'].create(wallet_category_vals)

    @api.model
    def _build_new_wallet_category_vals(self):
        default_wallet_product_categ_id = self.env.ref('wallet.category_default_wallets')
        default_wallet_product_id = self.env.ref('wallet.product_default_wallets')
        return {
            'name': 'Default wallet',
            'category_id': default_wallet_product_categ_id.id,
            'product_id': default_wallet_product_id.id,
        }

    @api.model
    def create(self, vals):
        if 'default_wallet_category_id' not in vals:
            new_wallet_category = self.create_new_wallet_category()
            vals['default_wallet_category_id'] = new_wallet_category.id

            company_id = super().create(vals)
            new_wallet_category.company_id = company_id.id
            return company_id
        else:
            return super().create(vals)
