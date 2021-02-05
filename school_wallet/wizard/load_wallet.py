# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class LoadWallet(models.TransientModel):
    _inherit = 'load.wallet'

    partner_person_type = fields.Selection(related='partner_id.person_type', store=True)
    student_invoice_address_ids = fields.Many2many('res.partner', related='partner_id.student_invoice_address_ids')

    invoice_address_id = fields.Many2one('res.partner')
    invoice_address_family_ids = fields.Many2many('res.partner', related='invoice_address_id.family_ids')

    family_id = fields.Many2one('res.partner')

    @api.depends('partner_id', 'invoice_address_id')
    @api.onchange('partner_id', 'invoice_address_id')
    def compute_payment_partner_id(self):
        for load_wallet in self:
            load_wallet.payment_partner_id = load_wallet.partner_id if load_wallet.partner_person_type != 'student' else load_wallet.invoice_address_id

    @api.onchange('partner_id', 'invoice_address_id')
    def refresh_payments(self):
        for load_wallet in self:
            load_wallet.payment_ids = False
            if load_wallet.invoice_address_id:
                family_ids = self.env['res.partner'].search([('is_family', '=', True), ('invoice_address_id', '=', load_wallet.invoice_address_id.id)])
                load_wallet.family_id = family_ids[0]

    def _build_load_wallet_with_payment_params(self):
        load_wallet_with_payment_params = super(LoadWallet, self)._build_load_wallet_with_payment_params()

        if self.partner_person_type == 'student':
            load_wallet_with_payment_params['move_params'] = {
                'student_id': self.partner_id.id,
                'family_id': self.family_id.id
                }

        return load_wallet_with_payment_params
