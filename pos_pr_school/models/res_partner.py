# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pos_student_invoice_payment_ids = fields.One2many('pos_pr.invoice.payment',
                                                      'student_id')
    pos_family_invoice_payment_ids = fields.One2many('pos_pr.invoice.payment',
                                                     'family_id')
