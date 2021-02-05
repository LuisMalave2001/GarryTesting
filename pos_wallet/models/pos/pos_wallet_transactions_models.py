# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class PosWalletWalletLoad(models.Model):
    _name = 'pos_wallet.wallet.load'

    amount = fields.Float()
    date = fields.Datetime()
    name = fields.Char()
    reconciled = fields.Boolean(default=False)

    partner_id = fields.Many2one('res.partner', required=True)
    load_partner_id = fields.Many2one('res.partner', compute='_compute_load_partner_id', required=True)
    payment_method_id = fields.Many2one('pos.payment.method', required=True)
    wallet_category_id = fields.Many2one('wallet.category', required=True)

    pos_session_id = fields.Many2one('pos.session', required=True)
    currency_id = fields.Many2one('res.currency', required=True, related='pos_session_id.currency_id')

    def _compute_load_partner_id(self):
        for record in self:
            record.load_partner_id = record._get_load_partner()

    def apply_loads(self):
        loadPartnerList = self.mapped('load_partner_id')
        loadsByLoadPartner = {partner: self.filtered(lambda load: load.load_partner_id == partner) for partner in loadPartnerList}
        pos_session_id = self.mapped('pos_session_id')
        pos_session_id.ensure_one()
        journal_id = pos_session_id.config_id.journal_id

        for partner_id, walletLoads in loadsByLoadPartner.items():
            move_id = walletLoads._create_miscellaneous_move(journal_id)
            wallet_lines = move_id.line_ids.filtered("pos_wallet_category_id")
            if not wallet_lines:
                raise exceptions.UserError("Something wrong when creating the misc move to pay the wallet")
            walletLoads._load_with_lines(wallet_lines)
            walletLoads.write({'reconciled': True})

    def _create_miscellaneous_move(self, journal_id):
        """
            This is complex for me, but
            The miscellaneous move has two parts,
            1) Lines with the debit with the sum of every payment method.
            2) Lines that will be used to reconcile any other move

            Later we need to create a statement for the payment method lines
         """
        payment_method_lines = self._generate_payment_method_lines()
        payment_receivable_lines = self._generate_wallet_receivable_lines()

        payment_miscellaneous_move_id = self.env['account.move'].create({
            'type': 'entry',
            'journal_id': journal_id.id,
            'line_ids': payment_method_lines + payment_receivable_lines
            })
        payment_miscellaneous_move_id.post()

        self._create_statements_and_reconcile_with_cash_line_ids(payment_miscellaneous_move_id.line_ids.filtered("is_payment_method_cash"))

        return payment_miscellaneous_move_id

    def _get_payment_method_amounts(self, cash=False):
        payment_method_ids = self.mapped('payment_method_id')
        if cash:
            payment_method_ids = payment_method_ids.filtered('is_cash_count')
        return {payment_method_id: sum(self.filtered(lambda wallet_loads: wallet_loads.payment_method_id == payment_method_id).mapped('amount')) for payment_method_id in
                payment_method_ids}

    def _generate_payment_method_lines(self):

        payment_method_amounts = self._get_payment_method_amounts()
        line_params = []
        for payment_method_id, amount in payment_method_amounts.items():
            line_params.append((0, 0, {
                'account_id': payment_method_id.receivable_account_id.id,
                'debit': amount,
                'name': payment_method_id.name,
                'is_payment_method_cash': payment_method_id.is_cash_count,
                'partner_id': False,
                }))
        return line_params

    def _generate_wallet_receivable_lines(self):
        line_params = []

        partner_ids = self.mapped("partner_id")
        for partner_id in partner_ids:
            partner_load_ids = self.filtered(lambda load: load.partner_id == partner_id)
            partner_receivable_id = partner_load_ids.mapped("pos_session_id").get_partner_receivable(partner_id.id)

            wallet_category_ids = partner_load_ids.mapped("wallet_category_id")
            payment_method_ids = partner_load_ids.mapped("payment_method_id")

            amount_by_category_and_method = []
            for wallet_category_id in wallet_category_ids:
                for payment_method_id in payment_method_ids:
                    wallet_load_ids = partner_load_ids.filtered(lambda wl: wl.wallet_category_id == wallet_category_id and wl.payment_method_id == payment_method_id)
                    if wallet_load_ids:
                        amount_by_category_and_method.append((wallet_category_id, payment_method_id, sum(wallet_load_ids.mapped("amount"))))

            for wallet_category_id, payment_method_id, amount in amount_by_category_and_method:
                line_params.append((0, 0, {
                    'partner_id': partner_id.id,
                    'account_id': partner_receivable_id.id,
                    'credit': amount,
                    'name': _('Wallet "%s" loaded with payment method "%s"') % (wallet_category_id.name, payment_method_id.name),
                    'pos_wallet_category_id': wallet_category_id.id
                    }))

        return line_params

    def _create_statements_and_reconcile_with_cash_line_ids(self, cash_line_ids):
        pos_session_id = self.pos_session_id.ensure_one()

        payment_method_amounts = self._get_payment_method_amounts(cash=True)
        statements_by_journal_id = {statement.journal_id.id: statement for statement in pos_session_id.statement_ids}

        lines_ids_to_reconcile = cash_line_ids

        for payment_method_id, amount in payment_method_amounts.items():

            statement = statements_by_journal_id[payment_method_id.cash_journal_id.id]

            statement_line_values = pos_session_id._get_statement_line_vals(statement, payment_method_id.receivable_account_id, amount)
            BankStatementLine = self.env['account.bank.statement.line']
            statement_line = BankStatementLine.create(statement_line_values)

            if not pos_session_id.config_id.cash_control:
                statement.write({
                    'balance_end_real': statement.balance_end
                    })

            statement.button_confirm_bank()
            if not statement_line.journal_entry_ids:
                statement_line.fast_counterpart_creation()
            lines_ids_to_reconcile += statement_line.journal_entry_ids.filtered(lambda aml: aml.account_id.internal_type == 'receivable')

        accounts = lines_ids_to_reconcile.mapped('account_id')
        lines_by_account = [lines_ids_to_reconcile.filtered(lambda l: l.account_id == account) for account in accounts]
        for lines in lines_by_account:
            lines.reconcile()

    def _get_load_partner(self):
        return self.mapped('partner_id')

    def _build_load_wallet_with_line_ids_params(self, line_ids, wallet_id, amount):
        return {
            'line_ids': line_ids.ids,
            'wallet_id': wallet_id.id,
            'amount': amount,
            }

    def _load_with_lines(self, wallet_line_ids):
        partner_id = self._get_load_partner()
        wallet_ids = wallet_line_ids.mapped('pos_wallet_category_id')
        for wallet_category_id in wallet_ids:
            line_ids = wallet_line_ids.filtered(lambda line_id: line_id.pos_wallet_category_id == wallet_category_id)
            amount = sum(self.filtered(lambda wallet_load_id: wallet_load_id.wallet_category_id == wallet_category_id).mapped('amount'))
            # partner_id.load_wallet_with_line_ids(line_ids=line_ids.ids, wallet_id=wallet_category_id.id, amount=amount)

            load_wallet_with_line_ids_params = self._build_load_wallet_with_line_ids_params(line_ids, wallet_category_id, amount)
            partner_id.load_wallet_with_line_ids(**load_wallet_with_line_ids_params)
