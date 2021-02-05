# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models, SUPERUSER_ID, exceptions

_logger = logging.getLogger(__name__)


def default_settings_values(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    default_surcharge_product_id = env['product.product']
    default_discount_product_id = env['product.product']

    try:
        default_surcharge_product_id = env.ref('pos_pr.default_surcharge_product')
        default_discount_product_id = env.ref('pos_pr.default_discount_product')
    except ValueError as e:
        _logger.error(e)

    env['ir.config_parameter'].set_param('pos_pr.surcharge_product_id', default_surcharge_product_id.id or '')
    env['ir.config_parameter'].set_param('pos_pr.discount_product_id', default_discount_product_id.id or '')

    for company in env['res.company'].search([]):
        env['pos.payment.method'].create({
            'name': 'Discount',
            'is_pos_pr_discount': True,
            'company_id': company.id,
        })


class Settings(models.TransientModel):
    """ Setting for surcharge """
    _inherit = "res.config.settings"

    pos_pr_surcharge_product_id = fields.Many2one("product.product", string="Surcharge Product",
                                                  config_parameter='pos_pr.surcharge_product_id')

    pos_pr_discount_product_id = fields.Many2one("product.product", string="Discount Product",
                                                 config_parameter='pos_pr.discount_product_id', )

    pos_pr_surcharge_default_amount = fields.Float(config_parameter='pos_pr.surcharge_default_amount')
    pos_pr_discount_default_account_id = fields.Many2one('account.account', string="Default discount account",
                                                         config_parameter='pos_pr.discount_default_account_id')

    def apply_surcharge_amount_to_sale_journals(self):
        self.env['account.journal'].search([('type', '=', 'sale')]).write({
            'surcharge_amount': self.pos_pr_surcharge_default_amount
        })

    def apply_surcharge_product_to_sale_journals(self):
        self.env['account.journal'].search([('type', '=', 'sale')]).write({
            'surcharge_product_id': self.pos_pr_surcharge_product_id.id
        })

    def recompute_surcharge_amounts(self):
        unpaid_invoices = self.env['account.move'].search([
            ('type', '=', 'out_invoice'),
            ('surcharge_invoice_id', '=', False),
            ('invoice_payment_state', '!=', 'paid')])
        unpaid_invoices.recompute_surcharge_amount()
