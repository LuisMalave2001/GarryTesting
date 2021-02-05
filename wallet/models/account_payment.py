# -*- coding: utf-8 -*-

from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.depends("reconciled_invoice_ids")
    def _compute_paid_amount(self):
        if self:
            payment_with_invoices = self.filtered('reconciled_invoice_ids')
            (self - payment_with_invoices).paid_amount = 0
            for payment_id in payment_with_invoices:
                payment_id.paid_amount = payment_id._get_all_reconciled_amount()

    def _get_all_reconciled_amount(self):
        self.ensure_one()
        foreign_currency = self.currency_id if self.currency_id != self.company_id.currency_id else False

        pay_term_line_ids = self.move_line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        partials = pay_term_line_ids.mapped(lambda l: l.matched_debit_ids + l.matched_credit_ids)
        amount = 0
        for partial in partials:
            if foreign_currency and partial.currency_id == foreign_currency:
                amount += partial.amount_currency
            else:
                amount += partial.company_currency_id._convert(partial.amount, self.currency_id, self.company_id, self.payment_date)
        return amount

    @api.depends("reconciled_invoice_ids")
    def _compute_unpaid_amount(self):
        for payment_id in self:
            payment_id.unpaid_amount = payment_id.amount - payment_id.paid_amount

    paid_amount = fields.Monetary(compute="_compute_paid_amount", store=True, default=0.0)
    unpaid_amount = fields.Monetary(compute="_compute_unpaid_amount", store=True)
    wallet_id = fields.Many2one("wallet.category")
