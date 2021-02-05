# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


class PosPrInvoicePayment(models.Model):
    _inherit = 'pos_pr.invoice.payment'

    student_id = fields.Many2one('res.partner', related="move_id.student_id", store=True)
    family_id = fields.Many2one('res.partner', compute="_compute_family_id", store=True)

    @api.depends('partner_id', 'move_id')
    def _compute_family_id(self):
        for payment in self:
            payment.family_id = (payment.partner_id
                                 if payment.partner_id.is_family
                                 else payment.move_id.family_id)


class InvoicePaymentSurcharge(models.Model):
    _inherit = 'pos_pr.invoice.surcharge'

    student_id = fields.Many2one('res.partner',
                                 domain='[("person_type", "=", "student")]')
    family_id = fields.Many2one('res.partner',
                                domain='[("is_family", "=", True)]')
