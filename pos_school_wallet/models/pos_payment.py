# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    student_id = fields.Many2one('res.partner', domain='[("person_type", "=", "student")]')
    family_id = fields.Many2one('res.partner', domain='[("is_family", "=", True)]')


class PosWalletWalletLoad(models.Model):
    _inherit = 'pos_wallet.wallet.load'

    student_id = fields.Many2one('res.partner', domain='[("person_type", "=", "student")]')
    family_id = fields.Many2one('res.partner', domain='[("is_family", "=", True)]')

    @api.model
    def create(self, vals):
        return super(PosWalletWalletLoad, self).create(vals)
