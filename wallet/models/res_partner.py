# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


def sort_by_wallet_hierarchy(line_tuple, wallet_position=0):
    wallet_id = line_tuple[wallet_position]
    parent_count = wallet_id.category_id.parent_count
    if wallet_id != wallet_id.default_wallet_category_id:
        parent_count += 1
    return parent_count


def sort_invoice_line_by_wallet_hierarchy(invoice_line_id):
    wallet_id = invoice_line_id.env["wallet.category"].get_wallet_by_category_id(invoice_line_id.product_id.categ_id)
    parent_count = wallet_id.category_id.parent_count
    if wallet_id != wallet_id.default_wallet_category_id():
        parent_count += 1
    return parent_count


class ResPartner(models.Model):
    _inherit = 'res.partner'

    json_dict_wallet_amounts = fields.Char(compute="_compute_json_dict_wallet_amounts", store=True)
    total_wallet_balance = fields.Monetary(string="Total Wallet Balance", compute="_compute_total_wallet_balance")

    def execute_autoclear(self):
        """ Just simulate a facts autoclear """

        # After some attempts, this is inneficient, because to simply some thins people can do
        # self.env['res.partner'].search([]).execute_autoclear()
        # If there is 2000, this will take a while. So we need just two things.
        #   If there is some payment
        #   If there is some invoice
        # by partner, this filter and will remove the empty result
        # I would like to use filtered, but I think what I want complex enough to do this without it

        partner_ids_list = self.mapped('id')

        partner_ids_with_payments = self.env["account.payment"].search(
            [("partner_id", 'in', partner_ids_list), ("unpaid_amount", ">", 0), ("state", "in", ["posted", "sent", "reconciled"])]).mapped('partner_id.id')
        partner_ids_with_credit_notes = self.env["account.move"].search(
            [("partner_id", 'in', partner_ids_list), ("invoice_payment_state", "!=", "paid"), ("state", "=", "posted"), ("type", "=", "out_refund")]).mapped('partner_id.id')
        partner_ids_with_invoices = self.env["account.move"].search(
            [("partner_id", 'in', partner_ids_list), ("invoice_payment_state", "!=", "paid"), ("state", "=", "posted"), ("type", "=", "out_invoice")]).mapped('partner_id.id')

        partner_ids_to_apply_autoclear = self.browse(set(partner_ids_with_payments + partner_ids_with_credit_notes + partner_ids_with_invoices))
        # partner_ids_to_apply_autoclear = self.browse(set(partner_ids_with_credit_notes))
        for partner in partner_ids_to_apply_autoclear:
            try:
                partner.autoload_payments_to_wallet()
                partner.autoload_credit_notes_to_wallet()
                partner.autopay_invoices_with_wallet()
            except Exception as err:
                raise err

    def autoload_credit_notes_to_wallet(self):
        for partner_id in self:
            partner_credit_note_ids = partner_id.get_unreconciled_credit_notes()
            if partner_credit_note_ids:
                credit_note_wallets_due = partner_credit_note_ids.get_wallet_due_amounts()
                credit_note_wallets_due = {self.env['wallet.category'].browse([wallet_id]): amount for wallet_id, amount in credit_note_wallets_due.items()}
                sorted_credit_note_wallet_dues = sorted(credit_note_wallets_due.items(), key=sort_by_wallet_hierarchy, reverse=True)

                for wallet_id, amount in sorted_credit_note_wallet_dues:
                    partner_id.load_wallet_with_credit_notes(partner_credit_note_ids, wallet_id, amount)

    def get_unreconciled_credit_notes(self):
        self.ensure_one()
        credit_note_ids = self.env["account.move"].search(
            [("partner_id", "=", self.id), ("invoice_payment_state", "!=", "paid"), ("state", "=", "posted"), ("type", "=", "out_refund")])
        return credit_note_ids

    def autopay_invoices_with_wallet(self):
        # Yes, I KNOW THAT I CAN USE INVOICE_IDS! But, in the future, we are going to make
        # the domain more complex and even with invoices that haven't their partner as customer
        for partner_id in self:
            move_ids = self.env["account.move"].search(
                [("partner_id", "=", partner_id.id), ("invoice_payment_state", "!=", "paid"), ("state", "=", "posted"), ("type", "=", "out_invoice")])
            move_ids_wallet_amounts = move_ids.get_available_wallet_amounts()
            if move_ids_wallet_amounts:
                partner_wallet_amounts = move_ids_wallet_amounts[partner_id]
                if sum(partner_wallet_amounts.values()):
                    move_ids.pay_with_wallet(partner_wallet_amounts)

    def autoload_payments_to_wallet(self):
        """ This will load payment to wallet automatically """
        for record in self:
            wallet_ids = self.env["wallet.category"].search([])
            payment_grouped = {}
            default_wallet_id = self.env.company.default_wallet_category_id

            # We find and group payment with wallets
            for wallet_id in wallet_ids:
                domain_payment_wallet_id = wallet_id.id
                if wallet_id == default_wallet_id:
                    domain_payment_wallet_id = False
                payment_ids = self.env["account.payment"].search(
                    [("partner_id", "=", self.id), ("unpaid_amount", ">", 0), ("wallet_id", "=", domain_payment_wallet_id), ("state", "in", ["posted", "sent", "reconciled"]), ])
                if payment_ids:
                    payment_grouped[wallet_id] = payment_ids

            # We start load wallet to partners
            for wallet_id, payment_ids in payment_grouped.items():
                amount = sum(payment_ids.mapped("unpaid_amount"))
                record.load_wallet_with_payments(payment_ids.ids, wallet_id.id, amount)
                logger.info("Wallet loaded to %s with: wallet_id: %s, payment_ids: %s, amount: %s" % (record, wallet_id, payment_ids, amount))

    def load_wallet_with_credit_notes(self, credit_note_ids, wallet_id, amount):
        """
        Load the wallet with credit notes, please, be sure that the amount is correctly
        :param credit_note_ids: credit notes that will pay the wallet
        :param wallet_id: the wallet to load
        :param amount: how much will be loaded.
        :return: the moves created to load wallet
        """
        self.ensure_one()
        move_ids = self.env["account.move"]
        wallet_env = self.env["wallet.category"]
        credit_note_ids = credit_note_ids.filtered(lambda credit_note: credit_note.invoice_payment_state != 'paid')

        credit_note_wallet_amounts_list = []
        for credit_note_id in credit_note_ids:
            credit_note_wallet_amounts = credit_note_id.get_wallet_due_amounts().items()
            for wallet, wallet_amount in credit_note_wallet_amounts:
                credit_note_wallet_amounts_list.append((credit_note_id, wallet_env.browse([wallet]), wallet_amount))

        sorted_credit_note_wallet_amounts_list = sorted(credit_note_wallet_amounts_list, key=lambda wt: sort_by_wallet_hierarchy(line_tuple=wt, wallet_position=1), reverse=True)
        for credit_note_id, credit_note_wallet_id, credit_note_wallet_amount in sorted_credit_note_wallet_amounts_list:

            if amount <= 0:
                break

            credit_note_amount_to_pay = credit_note_wallet_amount if credit_note_wallet_amount < amount else amount

            if credit_note_amount_to_pay:
                company_id = self.company_id or self.env.user.company_id

                move_id = self._create_wallet_move(wallet_id=wallet_id, amount=credit_note_amount_to_pay, company_id=company_id)
                move_id.post()

                move_receivable_line_id = move_id.line_ids.filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                credit_note_receivable_line_id = credit_note_id.line_ids.filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                move_receivable_line_id.account_id = credit_note_receivable_line_id.account_id
                move_id.js_assign_outstanding_line(credit_note_receivable_line_id.ids)

                # We do round(round(amount, 2) - round(credit_note_amounts, 2), 2)
                # to avoid 0.1 + 0.2 = 0.30000000000000004
                amount = round(round(amount, 2) - round(credit_note_amount_to_pay, 2), 2)
                move_ids += move_id

        return move_ids

    def load_wallet_with_payments(self, payment_ids: list, wallet_id: int, amount: float, **kwargs):
        self.ensure_one()
        o_payment_ids = self.env["account.payment"].browse(payment_ids)
        payments_receivable_line_ids = o_payment_ids.move_line_ids.filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')
        move_id = self.load_wallet_with_line_ids(**{
            'line_ids': payments_receivable_line_ids.ids,
            'wallet_id': wallet_id,
            'amount': amount,
            **kwargs
            })
        return move_id

    def load_wallet_with_line_ids(self, line_ids, wallet_id, amount, **kwargs):
        self.ensure_one()

        kwargs['partner_id'] = kwargs['partner_id'] if 'partner_id' in kwargs and kwargs['partner_id'] else self
        kwargs['move_params'] = kwargs['move_params'] if 'move_params' in kwargs and kwargs['move_params'] else {}

        if line_ids:
            o_line_ids = self.env["account.move.line"].browse(line_ids).filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')
            o_wallet_id = self.env["wallet.category"].browse([wallet_id])
            company_id = self.env.company
            move_id = self._create_wallet_move(o_wallet_id, amount, company_id, **kwargs)
            move_id.post()
            move_id.js_assign_outstanding_line(o_line_ids.ids)
            return move_id

    def _create_wallet_move(self, *args, **kwargs):
        return self.env['account.move'].create(self._build_wallet_move_params(*args, **kwargs))

    @api.model
    def _build_wallet_move_params(self, wallet_id, amount, company_id, **kwargs):
        return {
            "type": "out_invoice",
            "partner_id": kwargs['partner_id'].id,
            "journal_id": wallet_id.journal_category_id.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": wallet_id.product_id.id,
                "price_unit": amount,
                "quantity": 1,
                'company_id': company_id.id
                })],
            "company_id": company_id.id, **kwargs['move_params']
            }

    def _compute_total_wallet_balance(self):
        for partner in self:
            partner.total_wallet_balance = sum(partner
                                               .get_wallet_balances_dict([])
                                               .values()
                                               )

    @api.depends('invoice_ids')
    def _compute_json_dict_wallet_amounts(self):
        for partner_id in self:
            partner_id.json_dict_wallet_amounts = partner_id.get_wallet_balances_json([])

    def get_wallet_balances_json(self, wallet_id_list: typing.List[int]) -> str:
        """ :return A json with the wallet balances """

        self.ensure_one()
        return json.dumps(self.get_wallet_balances_dict(wallet_id_list))

    def get_wallet_balances_dict(self, wallet_id_list: typing.List[int]) -> dict:
        """ :return A dict with the wallet balances """

        self.ensure_one()
        wallet_categ_env = self.env["wallet.category"]
        wallet_category_ids = wallet_categ_env.browse(wallet_id_list) if wallet_id_list else wallet_categ_env.search([])
        dict_wallet_amounts = {}
        for wallet_category_id in wallet_category_ids:
            dict_wallet_amounts[wallet_category_id.id] = wallet_category_id.get_wallet_amount(self)
        return dict_wallet_amounts

    def action_open_wallet_history(self):
        self.ensure_one()
        action = self.env.ref("wallet.account_move_line_action_wallet_history").read()[0]
        wallets = self.env["wallet.category"].search([])
        products = wallets.mapped("product_id")
        action["domain"] = [("partner_id", "=", self.id), ("product_id", "in", products.ids)]
        return action
