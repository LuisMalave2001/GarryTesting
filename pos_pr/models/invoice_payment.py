# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class PosPR(models.Model):
    """ This model will save payments to invoices
        So we can use it for pay them when the session
        is closed """

    _name = 'pos_pr.invoice.payment'

    payment_group_id = fields.Many2one("pos_pr.payment_group")

    name = fields.Char()
    date = fields.Datetime()

    display_amount = fields.Float('Amount', compute='_compute_display_amount', store=True)
    payment_amount = fields.Float()
    payment_method_id = fields.Many2one("pos.payment.method")

    pos_session_id = fields.Many2one("pos.session", required=True)
    move_id = fields.Many2one("account.move", "Invoice", domain="[('type', '=', 'out_invoice')]", required=True)
    partner_id = fields.Many2one("res.partner", 'Customer', related='move_id.partner_id')

    invoice_address_id = fields.Many2one('res.partner', required=True, default=lambda self: self.partner_id)

    currency_id = fields.Many2one("res.currency", related="pos_session_id.currency_id")
    discount_amount = fields.Monetary()
    state = fields.Selection(
        [('draft', "Draft"),
         ('posted', "Posted"),
         ('cancelled', "Cancelled")],
        default='draft', string="State", required=True)

    @api.depends('payment_amount', 'discount_amount')
    def _compute_display_amount(self):
        for payment in self:
            payment.display_amount = payment.payment_amount + payment.discount_amount

    def cancel(self):
        self.write({'state': 'cancelled'})

    @api.model
    def create(self, vals):
        if "name" not in vals:
            name = self.env["ir.sequence"].next_by_code('seq.pos.payment.register.invoice.payment')
            vals["name"] = name

        if "state" not in vals or not vals['state']:
            vals.update(self.default_get(['state']))

        return super().create(vals)

    # Maybe I need to reimplement this mess :'(
    def pay_invoice(self):
        pos_session_ids = self.mapped("pos_session_id")
        for pos_session_id in pos_session_ids:
            journal_id = pos_session_id.config_id.journal_id
            payment_with_moves = pos_session_id.invoice_payment_ids.filtered('move_id')

            if payment_with_moves:
                invoice_payment_ids = payment_with_moves.filtered('payment_amount')
                discount_invoice_payment_ids = payment_with_moves.filtered('discount_amount')

    def reset_draft(self):
        self.write({'state': 'draft'})

    def write(self, vals):
        for payment in self:
            if not self._context.get('force_save', False) and payment.pos_session_id.state not in ['opened', 'closing_control']:
                raise exceptions.UserError(_("You cannot modify a invoice payment of a already closed pos session!"))
        return super(PosPR, self).write(vals)

    def _create_payment_miscellaneous_move(self, journal_id):
        payment_miscellaneous_move_id = self.env["account.move"].create({
            "journal_id": journal_id.id
        })

        journal_items = self._build_miscellaneous_moves_journal_items(payment_miscellaneous_move_id)
        receivable_per_invoice_and_partner = self._build_invoice_partner_receivable_journal_items(
            payment_miscellaneous_move_id)

        account_move_line_env = self.env["account.move.line"].with_context(check_move_validity=False)
        pos_line_ids = account_move_line_env.create(journal_items)
        pos_partner_invoice_receivable_line_ids = account_move_line_env.create(receivable_per_invoice_and_partner)

        payment_miscellaneous_move_id.post()

        pos_cash_line_ids = pos_line_ids.filtered("pos_payment_method_id.is_cash_count")

        return payment_miscellaneous_move_id, pos_cash_line_ids

    def _build_miscellaneous_moves_journal_items(self, move_id):
        payment_method_amounts = self._get_payment_method_amounts()
        journal_items = []

        for payment_method_id, amount in payment_method_amounts.items():
            payment_method_id = self.env["pos.payment.method"].browse([payment_method_id])
            receivable_account_id = payment_method_id.receivable_account_id

            journal_items.append({
                "account_id": receivable_account_id.id,
                "debit": amount,
                "name": payment_method_id.name,
                "move_id": move_id.id,
                "partner_id": False,
            })
        return journal_items

    def _build_invoice_partner_receivable_journal_items(self, move_id):
        journal_items = []

        for payment_id in self:
            payment_move_id = payment_id.move_id

            journal_items.append({
                "partner_id": payment_move_id.partner_id.id,
                "account_id": payment_move_id.get_receivable_account_ids()[0].id,
                "credit": payment_id.payment_amount,
                "name": _('%s to %s') % (payment_id.payment_method_id.name, payment_id.move_id.name),
                "move_id": move_id.id,
                "pos_payment_id": payment_id.id,
            })

        return journal_items

    def _create_statements_and_reconcile_with_cash_line_ids(self, cash_line_ids):
        pos_session_id = self.pos_session_id.ensure_one()

        payment_method_amounts = self._get_payment_method_amounts(cash=True)
        statements_by_journal_id = {statement.journal_id.id: statement for statement in pos_session_id.statement_ids}

        lines_ids_to_reconcile = cash_line_ids

        for payment_method_id, amount in payment_method_amounts.items():
            payment_method_id = self.env["pos.payment.method"].browse([payment_method_id])

            statement = statements_by_journal_id[payment_method_id.cash_journal_id.id]

            statement_line_values = pos_session_id._get_statement_line_vals(statement,
                                                                            payment_method_id.receivable_account_id,
                                                                            amount)
            BankStatementLine = self.env['account.bank.statement.line']
            statement_line = BankStatementLine.create(statement_line_values)

            if not pos_session_id.config_id.cash_control:
                statement.write({'balance_end_real': statement.balance_end})

            statement.button_confirm_bank()
            if not statement_line.journal_entry_ids:
                statement_line.fast_counterpart_creation()
            lines_ids_to_reconcile += statement_line.journal_entry_ids.filtered(
                lambda aml: aml.account_id.internal_type == 'receivable')

        accounts = lines_ids_to_reconcile.mapped('account_id')
        lines_by_account = [lines_ids_to_reconcile.filtered(lambda l: l.account_id == account) for account in accounts]
        for lines in lines_by_account:
            lines.reconcile()

    def _get_payment_method_amounts(self, cash=False):
        payment_method_amounts = {}

        payment_method_ids = self.mapped("payment_method_id")

        if cash:
            payment_method_ids = payment_method_ids.filtered("is_cash_count")

        for payment_method_id in payment_method_ids:
            payment_amount = sum(
                self.filtered(lambda invoice_payment: invoice_payment.payment_method_id == payment_method_id).mapped(
                    "payment_amount"))
            payment_method_amounts[payment_method_id.id] = payment_amount

        return payment_method_amounts

    def _reconcile_miscellaneous_move_with_invocies(self, move_id):
        # pos_session_id = self.pos_session_id.ensure_one()
        # invoice_ids = self.mapped("move_id")
        # invoice_receivable_lines = invoice_ids.get_receivable_line_ids()
        # payment_lines = move_id.line_ids.filtered(lambda line_id: line_id.account_id in invoice_receivable_lines.mapped("account_id") and line_id.partner_id)

        for payment_id in self:
            invoice_receivable_lines = payment_id.move_id.get_receivable_line_ids()
            payment_lines = move_id.line_ids.filtered(lambda line_id: line_id.pos_payment_id == payment_id)

            lines_by_account = invoice_receivable_lines + payment_lines

            accounts = lines_by_account.mapped('account_id')
            lines_by_account = [lines_by_account.filtered(lambda l: l.account_id == account) for account in accounts]
            for lines in lines_by_account:
                lines.reconcile()

    def _generate_invoice_discount(self):
        payments_with_discounts = self.filtered('discount_amount')

        for invoice_payment_id in payments_with_discounts:
            credit_note_vals = invoice_payment_id._build_credit_note_vals()
            credit_note = self.env["account.move"].create(credit_note_vals)
            credit_note.post()

            credit_note_receivable_line_ids = credit_note.get_receivable_line_ids()
            invoice_payment_id.move_id.js_assign_outstanding_line(credit_note_receivable_line_ids.id)

    def _build_credit_note_vals(self):
        """ Builds a credit note based on discount_amount field """
        self.ensure_one()

        discount_id = self.env['ir.config_parameter'].get_param('pos_pr.discount_product_id', 0)
        try:
            discount_product_id = self.env["product.product"].browse([int(discount_id)])
            if not discount_product_id:
                raise ValueError
        except ValueError:
            raise exceptions.UserError(_("You need to set up a discount product first"))

        # Checking if there is an default discount account
        # By default we set an empty record to discount_account_id
        # That way we discount_account_id.id will return False
        discount_account_id = self.env["account.account"]
        account_id = self.env['ir.config_parameter'].get_param('pos_pr.discount_default_account_id', 0)
        if account_id:
            try:
                discount_account_id = self.env["account.account"].browse([int(account_id)])
                if not discount_product_id:
                    discount_account_id = discount_product_id.property_account_income_id
            except ValueError:
                # int(account_id) can raise ValueError if there is an invalid value for pos_pr.discount_product_id
                # As we want it this to be optional, then we simply continue if there is some error
                # If it is false, we simply set it to its default value...
                pass

        return {
            "type": "out_refund",
            "partner_id": self.move_id.partner_id.id,
            "journal_id": self.move_id.journal_id.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": discount_product_id.id,
                "account_id": discount_account_id.id or discount_product_id.property_account_income_id.id,
                "price_unit": self.discount_amount,
                "quantity": 1,
            })],
        }
