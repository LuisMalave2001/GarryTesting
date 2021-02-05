# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountCashboxLine(models.Model):
    """ We add dynamic currency """
    _inherit = 'account.cashbox.line'

    # def _get_default_currency(self):
    #     currency_id = self.cashbox_id.currency_id
    #     if self.payment_method_id:
    #         currency_id = self.payment_method_id.cash_journal_id.currency_id \
    #                       or self.payment_method_id.cash_journal_id.company_id.currency_id
    #     return currency_id

    payment_method_id = fields.Many2one("pos.payment.method", _("Payment method"),
                                        domain="[('is_cash_count', '=', True)]")
    currency_id = fields.Many2one("res.currency", compute='_compute_currency_id', store=True)

    cashbox_currency_id = fields.Many2one('res.currency', related='cashbox_id.currency_id')
    converted_amount = fields.Monetary(compute='_compute_converted_amount', string='Amount currency', digits=0,
                                       readonly=True, currency_field='cashbox_currency_id')

    @api.model
    def create(self, vals):
        """ Computed currency """
        cashbox_line_ids = super().create(vals)
        cashbox_line_ids.compute_currency()
        return cashbox_line_ids

    def compute_currency(self):
        """ Compute the currency """
        for cashbox_line in self:
            if cashbox_line.payment_method_id:
                currency_id = cashbox_line.payment_method_id.cash_journal_id.currency_id \
                              or cashbox_line.payment_method_id.cash_journal_id.company_id.currency_id
                cashbox_line.currency_id = currency_id
            else:
                cashbox_line.currency_id = cashbox_line.cashbox_id.currency_id

    def recompute_converted_amount(self):
        """ Re Compute the converted currency """
        self.compute_currency()
        for cashbox_line in self:
            cashbox_line.converted_amount = cashbox_line.currency_id.compute(cashbox_line.subtotal, cashbox_line.cashbox_id.currency_id) or 0.0

    @api.onchange("payment_method_id")
    def _onchange_payment_method_id(self):
        self.compute_currency()

    @api.depends("payment_method_id")
    def _compute_currency_id(self):
        self.compute_currency()

    @api.depends("currency_id", 'subtotal')
    def _compute_converted_amount(self):
        self.recompute_converted_amount()


class AccountBankStmtCashWizard(models.Model):
    """
    Account Bank Statement popup that allows entering cash details.
    """
    _inherit = 'account.bank.statement.cashbox'

    @api.depends('cashbox_lines_ids')
    def _recompute_line_ids_currencies(self):
        for cashbox in self:
            cashbox.cashbox_lines_ids.compute_currency()

    @api.depends('cashbox_lines_ids', 'cashbox_lines_ids.coin_value', 'cashbox_lines_ids.number')
    def _compute_total(self):
        for cashbox in self:
            cashbox.cashbox_lines_ids.compute_currency()
            current_currency_id = self.currency_id
            cashbox.total = sum([line.currency_id.compute(from_amount=line.subtotal, to_currency=current_currency_id)
                                 for line in cashbox.cashbox_lines_ids])
