# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class PaymentGroup(models.Model):
    """ This payment group is used for reports """
    _name = "pos_pr.payment_group"
    _description = 'Payments groups'

    name = fields.Char(string='Name')
    invoice_payment_ids = fields.One2many("pos_pr.invoice.payment", "payment_group_id", string="Payments")
    payment_amount_total = fields.Monetary(compute='_compute_amount_total', store=True)
    payment_change = fields.Monetary()

    partner_id = fields.Many2one('res.partner', required=True)
    date = fields.Datetime()

    pos_session_id = fields.Many2one('pos.session', required=True)
    currency_id = fields.Many2one('res.currency', related='pos_session_id.currency_id')

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.pos.payment.register.invoice.payment_group')
        if 'date' not in vals:
            vals['date'] = fields.Datetime.to_string(fields.Datetime.now())

        return super().create(vals)

    @api.depends('invoice_payment_ids', 'invoice_payment_ids.state')
    def _compute_amount_total(self):
        for payment_group_id in self:
            payment_amount_total = sum(payment_group_id.invoice_payment_ids.filtered(lambda p: p.state != 'cancelled').mapped('payment_amount'))
            payment_group_id.payment_amount_total = payment_amount_total
