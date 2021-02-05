# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import fields, models, api, _


class PosSession(models.Model):
    _inherit = "pos.session"

    invoice_payment_ids = fields.One2many("pos_pr.invoice.payment", "pos_session_id")
    invoice_surcharge_ids = fields.One2many("pos_pr.invoice.surcharge", "pos_session_id")

    invoice_payment_groups_ids = fields.Many2many('pos_pr.payment_group', compute='_compute_invoice_payment_groups_ids', store=True)

    invoice_payment_amount = fields.Float(compute='_compute_cash_balance')
    invoice_payment_move_id = fields.Many2one("account.move", string="Invoice payment misc move")

    @api.depends('invoice_payment_ids')
    def _compute_invoice_payment_groups_ids(self):
        for pos_session in self:
            pos_session.invoice_payment_groups_ids = pos_session.invoice_payment_ids.filtered(lambda payment: payment.state != 'cancelled').mapped('payment_group_id')

    def json_get_paid_surcharge_by_customer(self):
        self.ensure_one()
        partner_ids = self.invoice_surcharge_ids.mapped("partner_id")
        json_paid_surcharge_by_customer = {partner_id.id: sum(self.invoice_surcharge_ids.filtered(lambda surcharge: surcharge.partner_id == partner_id).mapped('amount')) for
                                           partner_id in partner_ids}
        return json_paid_surcharge_by_customer

    def _validate_session(self):
        action = super()._validate_session()
        if self.invoice_surcharge_ids:
            self.invoice_surcharge_ids.apply_surcharge()

            payment_ids = list(set(self.invoice_payment_ids.ids) | set(self.invoice_surcharge_ids.payment_ids.ids))

            self.invoice_payment_ids = payment_ids
        if self.invoice_payment_ids:
            self._create_payment_register_invoices_payment()
            self._create_invoices_discount()
            not_cacelled_payment_ids = self.invoice_payment_ids.filtered(lambda payment: payment.state != 'cancelled')
            not_cacelled_payment_ids.with_context({'force_save': True}).write({'state': 'posted'})
            not_cacelled_payment_ids.mapped('move_id')._compute_pos_pr_paid_amount()
        return action

    def _create_payment_register_invoices_payment(self):
        invoice_payment_ids = self.invoice_payment_ids.filtered(lambda payment: payment.state != 'cancelled' and payment.payment_amount)
        if invoice_payment_ids:
            journal = self.config_id.journal_id
            account_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
                'journal_id': journal.id,
                'date': fields.Date.context_today(self),
                'ref': self.name,
                })
            self.write({
                'invoice_payment_move_id': account_move.id
                })

            # Cash reconcile lines
            MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)

            # Debit lines
            invoice_payment_ids.filtered('')
            payment_move_line_vals = MoveLine.create(self._get_payment_move_line_vals_list(invoice_payment_ids.filtered(lambda p: not p.payment_method_id.is_cash_count)))
            cash_reconcile_lines = MoveLine.create(self._get_payment_move_line_vals_list(invoice_payment_ids.filtered('payment_method_id.is_cash_count')))
            print(payment_move_line_vals)

            # Crear statements lines
            statement_line_vals = self._get_pr_statement_line_vals(invoice_payment_ids)
            cash_statement_lines = {}
            for statement in self.statement_ids:
                statement.button_reopen()
                cash_statement_lines[statement] = self.env['account.bank.statement.line'].create(statement_line_vals[statement])
                if not self.config_id.cash_control:
                    statement.write({'balance_end_real': statement.balance_end})

                statement.button_confirm_bank()
                for statement_line in cash_statement_lines[statement]:
                    if not statement_line.journal_entry_ids:
                        statement_line.fast_counterpart_creation()
                        cash_reconcile_lines += statement_line.journal_entry_ids.filtered(lambda aml: aml.account_id.internal_type == 'receivable')

            # Invoices Receivable lines
            misc_move_receivable_lines = MoveLine.create(self._get_pr_receivable_line_vals_list(invoice_payment_ids))

            account_move.post()
            # Post and reconcile entries
            # Cash
            accounts = cash_reconcile_lines.mapped('account_id')
            lines_by_account = [cash_reconcile_lines.filtered(lambda l: l.account_id == account) for account in accounts]
            for lines in lines_by_account:
                lines.reconcile()

            # Invoices
            for invoice in invoice_payment_ids.mapped('move_id'):
                payment_ids = invoice_payment_ids.filtered(lambda invPay: invPay.move_id == invoice)
                invoice_receivable_lines = invoice.get_receivable_line_ids()
                payment_lines = misc_move_receivable_lines.filtered(lambda line_id: line_id.pos_payment_id.id in payment_ids.ids)

                lines_by_account = invoice_receivable_lines + payment_lines

                accounts = lines_by_account.mapped('account_id')
                lines_by_account = [lines_by_account.filtered(lambda l: l.account_id == account) for account in accounts]
                for lines in lines_by_account:
                    lines.reconcile()

    def _create_invoices_discount(self):
        discount_payment_ids = self.invoice_payment_ids.filtered(lambda payment: payment.state != 'cancelled' and payment.discount_amount)
        discount_payment_ids._generate_invoice_discount()

    def _get_payment_move_line_vals_list(self, invoice_payment_ids):
        return invoice_payment_ids.mapped(self._get_payment_move_line_vals)

    def _get_payment_move_line_vals(self, invoice_payment_id):

        amount = invoice_payment_id.payment_amount

        date = invoice_payment_id.date or fields.Datetime.now().date()
        amount_converted = self.currency_id._convert(amount, self.company_id.currency_id, self.company_id, date, round=True)

        line_vals = {
            'account_id': invoice_payment_id.payment_method_id.receivable_account_id.id,
            'move_id': self.invoice_payment_move_id.id,
            # 'partner_id': self.env["res.partner"]._find_accounting_partner(invoice_payment_id.invoice_address_id).id,
            'name': '%s - %s' % (self.name, invoice_payment_id.payment_method_id.name),
            }
        return self._debit_amounts(line_vals, amount, amount_converted)

    def _get_pr_statement_line_vals(self, invoice_payment_ids):
        statement_line_vals = defaultdict(list)
        statements_by_journal_id = {statement.journal_id.id: statement for statement in self.statement_ids}
        for invoice_payment_id in invoice_payment_ids.filtered('payment_method_id.is_cash_count'):
            statement = statements_by_journal_id[invoice_payment_id.payment_method_id.cash_journal_id.id]
            statement_line_vals[statement].append(
                self._get_statement_line_vals(statement, invoice_payment_id.payment_method_id.receivable_account_id, invoice_payment_id.payment_amount, invoice_payment_id.date))
        return statement_line_vals

    def _get_pr_receivable_line_vals_list(self, invoice_payment_ids):
        return invoice_payment_ids.mapped(self._get_pr_receivable_line_vals)

    def _get_pr_receivable_line_vals(self, invoice_payment_id):
        amount = invoice_payment_id.payment_amount

        date = invoice_payment_id.date
        amount_converted = self.currency_id._convert(amount, self.company_id.currency_id, self.company_id, date, round=True)

        receivable_lines = {
            "partner_id": invoice_payment_id.move_id.partner_id.id,
            "account_id": invoice_payment_id.move_id.get_receivable_account_ids()[0].id,
            "name": _('%s to %s') % (invoice_payment_id.payment_method_id.name, invoice_payment_id.move_id.name),
            "move_id": self.invoice_payment_move_id.id,
            "pos_payment_id": invoice_payment_id.id,
            }
        return self._credit_amounts(receivable_lines, amount, amount_converted)

    def _create_account_move(self):
        """ Create account.move and account.move.line records for this session.

        Side-effects include:
            - setting self.move_id to the created account.move record
            - creating and validating account.bank.statement for cash payments
            - reconciling cash receivable lines, invoice receivable lines and stock output lines
        """

        journal = self.config_id.journal_id
        # Passing default_journal_id for the calculation of default currency of account move
        # See _get_default_currency in the account/account_move.py.
        account_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
            'journal_id': journal.id,
            'date': fields.Date.context_today(self),
            'ref': self.name,
            })
        self.write({
            'move_id': account_move.id
            })

        data = {}
        data = self._accumulate_amounts(data)
        data = self._create_non_reconciliable_move_lines(data)
        data = self._create_cash_statement_lines_and_cash_move_lines(data)

        # We need to clear partner due it causes that the partner ledger goes wrong
        self.move_id.line_ids.with_context(check_move_validity=False).partner_id = False

        # Now here is where we add the partner to the receivable lines
        # Thanks odoo!

        data = self._create_invoice_receivable_lines(data)
        data = self._create_stock_output_lines(data)
        data = self._create_extra_move_lines(data)
        data = self._reconcile_account_move_lines(data)

    def _create_invoice_receivable_lines(self, data):

        MoveLine = data.get('MoveLine')
        payment_move_line_values = self._build_payment_receivable_lines()
        invoice_receivable_lines = {}

        payment_move_line_ids = MoveLine.create(payment_move_line_values)
        for account_id in payment_move_line_ids.mapped("account_id"):
            invoice_receivable_lines[account_id.id] = payment_move_line_ids.filtered(lambda line: line.account_id == account_id)

        data.update({
            "invoice_receivable_lines": invoice_receivable_lines
            })

        return data

    def _build_payment_receivable_lines(self):
        self.ensure_one()
        grouped_invoice_payments = self._group_invoice_payments()
        payment_receivable_lines = self._build_payments_move_line_values(grouped_invoice_payments)
        return payment_receivable_lines

    def _group_invoice_payments(self):
        grouped_invoice_payments = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
            'amount': 0.0,
            'amount_converted': 0.0
            })))

        for order_id in self.order_ids.filtered(lambda order: order.is_invoiced):
            for payment_id in order_id.payment_ids:
                amount = payment_id.amount
                date = payment_id.payment_date
                receivalbe_account_id = order_id.get_receivable_account()
                payment_method_id = payment_id.payment_method_id

                partner_id = self.env["res.partner"]._find_accounting_partner(order_id.partner_id)

                new_amount = self._update_amounts(grouped_invoice_payments[partner_id][receivalbe_account_id][payment_method_id], {
                    'amount': amount
                    }, date)

                grouped_invoice_payments[partner_id][receivalbe_account_id][payment_method_id] = new_amount

        return grouped_invoice_payments

    def _build_payments_move_line_values(self, grouped_invoice_payments):
        # invoice_receivable_vals = defaultdict(lambda: defaultdict(list))
        payment_move_lines = []
        for partner_id, partner_amounts in grouped_invoice_payments.items():
            for receivable_account_id, receivable_amounts in partner_amounts.items():
                for payment_method_id, amounts in receivable_amounts.items():
                    receivable_line_vals = self._get_invoice_receivable_vals(receivable_account_id.id, amounts['amount'], amounts['amount_converted'])

                    # If partner doesn't have company, partner_id in the receivable account will be different

                    resposible_partner_id = self.env["res.partner"]._find_accounting_partner(partner_id)

                    receivable_line_vals["pos_payment_method_id"] = payment_method_id.id
                    receivable_line_vals["partner_id"] = resposible_partner_id.id

                    # invoice_receivable_vals[partner_id][receivable_account_id].append(receivable_line_vals)
                    payment_move_lines.append(receivable_line_vals)
        return payment_move_lines

    @api.depends('payment_method_ids', 'order_ids', 'cash_register_balance_start', 'cash_register_id', 'invoice_payment_ids')
    def _compute_cash_balance(self):
        super()._compute_cash_balance()
        for session in self:
            cash_payment_method_ids = session.payment_method_ids.filtered('is_cash_count')

            if cash_payment_method_ids:
                cash_payment_method_ids = cash_payment_method_ids[1:]
                transaction_total_amount = session.get_remain_cash_transaction_total_amount(cash_payment_method_ids=cash_payment_method_ids)
                total_cash_invoice_payment_amount = 0.0 if session.state == 'closed' else sum(
                    session.invoice_payment_ids.filtered(lambda payment: payment.state != 'cancelled' and payment.payment_method_id.is_cash_count).mapped("payment_amount"))

                cash_register_total_entry_encoding = 0.0 if session.state == 'closed' else transaction_total_amount + total_cash_invoice_payment_amount

                session.cash_register_total_entry_encoding += cash_register_total_entry_encoding
                session.invoice_payment_amount = sum(session.invoice_payment_ids.filtered(lambda payment: payment.state != 'cancelled').mapped("display_amount"))
                session.cash_register_balance_end += cash_register_total_entry_encoding
                session.cash_register_difference -= cash_register_total_entry_encoding
            else:
                session.invoice_payment_amount = 0.0

    def get_remain_cash_transaction_total_amount(self, cash_payment_method_ids):
        self.ensure_one()
        cash_register_total_entry_encoding = 0.0

        for cash_payment_method in cash_payment_method_ids:
            total_cash_payment = sum(self.order_ids.mapped('payment_ids').filtered(lambda payment: payment.payment_method_id == cash_payment_method).mapped('amount'))
            cash_register_total_entry_encoding += total_cash_payment
        return cash_register_total_entry_encoding
