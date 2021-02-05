# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """ Added some field to easier point of sale javascript """
    _inherit = "account.move"

    @api.model
    def _default_surcharge_amount(self):
        return self._get_default_journal().surcharge_amount
        # for move_id in self:
        #     move_id.surcharge_amount = move_id.journal_id.surcharge_amount

    def recompute_surcharge_amount(self):
        for move_id in self:
            move_id.surcharge_amount = move_id.journal_id.surcharge_amount

    surcharge_invoice_id = fields.Many2one("account.move", "Surcharge Invoice")
    surcharge_amount = fields.Monetary(default=_default_surcharge_amount)
    is_overdue = fields.Boolean(compute="_compute_is_overdue", default=False)
    is_overdue_stored = fields.Boolean(compute="_compute_is_overdue_stored", store=True, default=False)
    pos_pr_payment_ids = fields.One2many("pos_pr.invoice.payment", "move_id", domain=[('state', '!=', 'cancelled')])

    pos_pr_paid_amount = fields.Float(compute="_compute_pos_pr_paid_amount", store=True)

    @api.depends("pos_pr_payment_ids", "pos_pr_payment_ids.state")
    def _compute_pos_pr_paid_amount(self):
        for move_id in self:
            not_closed_payments = move_id.pos_pr_payment_ids.filtered(lambda payment: payment.pos_session_id.state in ['opened', 'closing_control'])
            move_id.pos_pr_paid_amount = sum(not_closed_payments.mapped(lambda payment: payment.display_amount) or [0])

    def _compute_is_overdue(self):
        for move_id in self:
            today = datetime.today()

            if move_id.invoice_date_due:
                move_id.is_overdue = move_id.invoice_date_due < today.date()
            else:
                move_id.is_overdue = False

    @api.depends("is_overdue")
    def _compute_is_overdue_stored(self):
        for move_id in self:
            move_id.is_overdue_stored = move_id.is_overdue

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'type' in vals and vals['type'] == 'out_invoice' and 'surcharge_amount' not in vals:
                journal_id = self.env['account.journal'].browse([vals['journal_id']]) if 'journal_id' in vals and vals['journal_id'] else self._get_default_journal()
                vals['surcharge_amount'] = journal_id.surcharge_amount
        return super().create(vals_list)


class AccountMoveLine(models.Model):
    """ Added some metadata to move lines """
    _inherit = 'account.move.line'

    pos_payment_method_id = fields.Many2one("pos.payment.method", 'POS Payment method')
    pos_payment_id = fields.Many2one("pos_pr.invoice.payment", 'POS Invoice Payment')
