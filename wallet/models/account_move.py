# -*- coding: utf-8 -*-
import typing
from odoo import fields, models, api, exceptions, _
from collections import defaultdict

import logging
import math

_logger = logging.getLogger(__name__)

WalletDict = typing.Dict[int, float]


def sort_by_wallet_hierarchy(line_tuple):
    wallet_id = line_tuple[0]
    parent_count = wallet_id.category_id.parent_count
    if wallet_id != wallet_id.default_wallet_category_id:
        parent_count += 1
    return parent_count


class AccountMove(models.Model):
    """ Adds wallet features:
        Todo: We need to write this better... Because if there is a bug, it will be really hard to see it.
    """
    _inherit = 'account.move'

    def is_wallet_payment(self):
        self.ensure_one()
        product_ids = self.mapped("invoice_line_ids").mapped("product_id")
        for product_id in product_ids:
            if product_id in self.env["wallet.category"].search([]).mapped("product_id"):
                return True
        return False

    def get_wallet_paid_amounts(self):
        self.ensure_one()
        wallet_amount_to_apply = defaultdict(float)
        default_wallet = self.env.company.default_wallet_category_id
        for reconcile_json in self._get_reconciled_info_JSON_values():
            reconcile_move_id = self.env["account.move"].browse([reconcile_json["move_id"]])
            if reconcile_json["account_payment_id"] or not reconcile_move_id.is_wallet_payment():
                wallet_amount_to_apply[default_wallet] += reconcile_json["amount"]
            else:
                move_invoice_line_ids = reconcile_move_id.mapped("invoice_line_ids")
                if move_invoice_line_ids:
                    for wallet_id, amount in move_invoice_line_ids.mapped(lambda line: (
                            self.env["wallet.category"].search([("product_id", "=", line.product_id.id)]),
                            line.price_total)):
                        wallet_amount_to_apply[wallet_id] += amount
        return dict(wallet_amount_to_apply)

    def get_wallet_raw_due_amounts(self):
        self.ensure_one()
        invoice_line_ids = self.mapped("invoice_line_ids")
        tuple_list_category_amount = invoice_line_ids.mapped(
            lambda invoice_line_id: (self.env["wallet.category"].
                                     get_wallet_by_category_id(invoice_line_id.product_id.categ_id),
                                     invoice_line_id.price_total))
        current_invoices_category_amounts = defaultdict(float)
        for category_id, amount in tuple_list_category_amount:
            current_invoices_category_amounts[category_id] += amount
        return dict(current_invoices_category_amounts)

    def get_wallet_due_amounts(self):

        all_wallet_due_amounts = defaultdict(float)
        for move_id in self:
            # Getting the due amount without payments
            wallet_raw_due_amounts = move_id.get_wallet_raw_due_amounts()
            wallet_due_amounts = dict(wallet_raw_due_amounts)

            # Getting how much has been paid with wallets
            wallet_paid_amounts = defaultdict(float, move_id.get_wallet_paid_amounts())
            if wallet_paid_amounts:
                # Sorting them by wallet hierarchy, this part is crucial
                sorted_wallet_raw_due_amounts = sorted(wallet_raw_due_amounts.items(), key=sort_by_wallet_hierarchy,
                                                       reverse=True)

                for wallet_id, amount in sorted_wallet_raw_due_amounts:
                    looking_wallet = wallet_id
                    while amount > 0:
                        looking_wallet_amount = wallet_paid_amounts[looking_wallet]
                        if looking_wallet_amount > 0:
                            wallet_remove_amount = amount

                            if looking_wallet_amount - amount < 0:
                                wallet_remove_amount = looking_wallet_amount

                            wallet_paid_amounts[looking_wallet] = wallet_paid_amounts[
                                                                      looking_wallet] - wallet_remove_amount
                            amount = amount - wallet_remove_amount

                            wallet_due_amounts[wallet_id] = wallet_due_amounts[wallet_id] - wallet_remove_amount
                        if looking_wallet.is_default_wallet:
                            break
                        looking_wallet = wallet_id.get_wallet_by_category_id(looking_wallet.category_id.parent_id)

            for wallet_id, amount in wallet_due_amounts.items():
                all_wallet_due_amounts[wallet_id.id] = all_wallet_due_amounts[wallet_id.id] + amount

        return all_wallet_due_amounts

    def pay_with_wallet(self, wallet_payment_dict):
        """
        wallet_payment_dict: should be a dict with the form {wallet_id(int): amount(float),...}
        this method only work for invoices that has the same partner_id.

        this method order automatically per date

        TODO: Be able to do move_ids.pay_with_wallet(wallet_payment_dict) where those move_ids has different customers
        """
        move_ids = self.sort_by_setting_field()
        wallet_ids = self.env['wallet.category'].browse(wallet_payment_dict.keys())
        partner_id = self.mapped("partner_id")
        partner_id.ensure_one()
        partner_current_balances = partner_id.get_wallet_balances_dict([])

        for move_id in move_ids:
            _logger.info('Paying %s with wallet: %s' % (move_id.name, wallet_payment_dict))
            amounts_to_pay = move_id.get_wallet_payment_distribution(wallet_payment_dict, partner_current_balances)

            # If someone can find a shorter way to update wallet_payment_dict with the new values, please, help me ;-;
            for wallet_id, amount in amounts_to_pay.items():
                partner_current_balances[wallet_id] -= amount

            amounts_to_pay = {self.env['wallet.category'].browse([wallet_id]): amount for wallet_id, amount in
                              amounts_to_pay.items()}
            if sum(amounts_to_pay.values()):
                journal_ids = set(map(lambda w: w.journal_category_id, amounts_to_pay.keys()))
                for journal_id in journal_ids:
                    filtered_wallet_line_ids = {wallet_id: amount for wallet_id, amount in amounts_to_pay.items() if
                                                wallet_id.journal_category_id == journal_id and amount}

                    if filtered_wallet_line_ids:

                        invoice_line_ids = []
                        for wallet_id, amount in filtered_wallet_line_ids.items():

                            # We check if there is available wallet
                            wallet_amount = wallet_id.get_wallet_amount(partner_id)
                            if wallet_amount >= -abs(wallet_id.credit_limit):

                                invoice_line_ids.append((0, 0, {
                                    "product_id": wallet_id.product_id.id,
                                    "account_id": wallet_id.account_id.id,
                                    "price_unit": amount,
                                    "quantity": 1,
                                }))
                            else:
                                raise exceptions.ValidationError(
                                    _("You are trying to pay %s in %s when there is only %s available") % (
                                        amount, wallet_id.name, wallet_amount))

                        credit_note_id = self.create(
                            move_id.get_wallet_credit_note_values(
                                partner_id,
                                journal_id,
                                invoice_line_ids)
                            )

                        # We need to ensure that the credit note has the same receivable than the invoice
                        # So we force it
                        move_receivable_line_id = move_id.line_ids. \
                            filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                        receivable_line_id = credit_note_id.line_ids. \
                            filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                        receivable_line_id.account_id = move_receivable_line_id.account_id

                        credit_note_id.post()
                        _logger.info("Invoice [%s]: %s paid to %s with: credit note [%s]: %s, amount: %s" %
                                     (move_id.id, move_id.name, partner_id,
                                      credit_note_id.id, credit_note_id.name, credit_note_id.amount_total))
                        move_id.js_assign_outstanding_line(receivable_line_id.id)
            _logger.info('Paid %s with wallet: %s' % (move_id.name, wallet_payment_dict))

        wallet_payment_dict = {self.env['wallet.category'].browse([wallet_id]): amount for wallet_id, amount in
                               wallet_payment_dict.items()}
        wallet_ids = self.env["wallet.category"].browse(
            set(map(lambda wallet_id: wallet_id.id, wallet_payment_dict.keys())))
        wallet_ids.sorted(lambda wallet_id: wallet_id.category_id.parent_count, reverse=True)
        for wallet_id in wallet_ids:
            wallet_amount = wallet_id.get_wallet_amount(partner_id)
            if wallet_amount < -abs(wallet_id.credit_limit):
                raise exceptions.ValidationError(
                    _("[%s] Wallet will have a final amount of [%s]!. Credit limit: %s") % (
                        wallet_id.name, wallet_amount, wallet_id.credit_limit))


    def get_wallet_credit_note_values(self, partner_id, journal_id, invoice_line_ids):
        self.ensure_one()
        return {
            "type": "out_refund",
            "partner_id": partner_id,
            "journal_id": journal_id.id,
            "invoice_line_ids": invoice_line_ids,
        }

    def sort_by_setting_field(self):
        """ :return The moves sorted by a field setted in setting view """
        return self.sorted(lambda m: m.invoice_date_due or m.invoice_date)

    def get_wallet_payment_distribution(self, wallet_payment_dict: WalletDict, partner_current_balances=False) -> WalletDict:
        partner_id = self.mapped("partner_id")
        partner_id.ensure_one()
        wallet_payment_dict_env = {self.env['wallet.category'].browse([wallet_id]): amount for wallet_id, amount in
                               wallet_payment_dict.items()}
        wallet_due_amounts = {self.env['wallet.category'].browse([wallet_id]): amount for wallet_id, amount in
                              self.get_wallet_due_amounts().items()}
        sorted_wallet_due_amounts = sorted(wallet_due_amounts.items(), key=sort_by_wallet_hierarchy, reverse=True)
        partner_wallet_amounts = partner_current_balances or partner_id.get_wallet_balances_dict([])

        amounts_to_pay_dict = defaultdict(int)
        for wallet_id, due_amount in sorted_wallet_due_amounts:
            looking_wallet = wallet_id
            looking_payment_wallet = wallet_id
            while due_amount > 0:
                if looking_payment_wallet not in wallet_payment_dict_env:
                    looking_payment_wallet = looking_wallet.get_wallet_by_category_id(looking_payment_wallet.category_id.parent_id)
                    continue

                amount = wallet_payment_dict_env[looking_payment_wallet]

                # Here we check how much it can pay
                partner_wallet_amount = partner_wallet_amounts[looking_wallet.id]
                wallet_limit_payment_amount = abs(-abs(looking_wallet.credit_limit)-partner_wallet_amount)
                amount_to_pay = min(wallet_limit_payment_amount, amount, due_amount)

                # Now we added to the dict
                amounts_to_pay_dict[looking_wallet.id] += amount_to_pay

                # And we reduce some value to "simulate" the payment
                due_amount -= amount_to_pay
                wallet_payment_dict_env[looking_payment_wallet] -= amount_to_pay
                wallet_payment_dict[looking_payment_wallet.id] -= amount_to_pay

                if looking_wallet == self.env.company.default_wallet_category_id:
                    break
                looking_wallet = looking_wallet.get_wallet_by_category_id(looking_wallet.category_id.parent_id)
        return amounts_to_pay_dict

    def get_available_wallet_amounts(self):
        """ This will return an array of dicts
            [
                "partner_1": {wallet_things},
                "partner_2": {wallet_things2},
            ]
         """
        partner_ids_wallet_amounts = {}
        if self:
            partner_ids = self.mapped("partner_id")
            for partner_id in partner_ids:
                move_ids = self.filtered(lambda move: move.partner_id == partner_id).sorted(lambda m: m.invoice_date_due or m.invoice_date)
                walletCategoryEnv = self.env["wallet.category"]

                # Getting how much we can pay
                all_wallet_ids = walletCategoryEnv.search([])
                partner_wallet_amounts = {wallet_id.id: wallet_id.get_wallet_amount(partner_id)
                                          for wallet_id in all_wallet_ids}

                # Now we perform the operations
                wallet_to_apply = defaultdict(float)
                for move_id in move_ids:
                    move_wallet_amounts = move_id.get_wallet_due_amounts()
                    amounts_to_pay = self.calculate_wallet_distribution(move_wallet_amounts, partner_wallet_amounts)
                    for wallet_id, amount in amounts_to_pay.items():
                        wallet_to_apply[wallet_id.id] += amount

                # wallet_to_apply = self.calculate_wallet_distribution(current_invoices_category_amounts,
                # partner_wallet_amounts)
                partner_ids_wallet_amounts.update({partner_id: dict(wallet_to_apply)})
        return partner_ids_wallet_amounts

    def calculate_wallet_distribution(self, wallet_dict_to_pay, wallet_dict_available):
        """ Calculate de distrubtion of wallet amounts using their hierarchy """

        wallet_dict_to_pay = {self.env['wallet.category'].browse([wallet_id]): amount for wallet_id, amount in
                              wallet_dict_to_pay.items()}
        wallet_dict_available = {self.env['wallet.category'].browse([wallet_id]): amount for wallet_id, amount in
                                 wallet_dict_available.items()}

        sorted_wallet_dict_to_pay = sorted(wallet_dict_to_pay.items(), key=sort_by_wallet_hierarchy, reverse=True)
        wallet_amount_to_apply = defaultdict(float)
        for wallet_id, amount in sorted_wallet_dict_to_pay:
            looking_wallet = wallet_id
            while amount > 0:
                if looking_wallet in wallet_dict_available:
                    looking_wallet_amount = wallet_dict_available[looking_wallet]
                    if looking_wallet_amount > -abs(wallet_id.credit_limit):
                        wallet_remove_amount = amount

                        if looking_wallet_amount - amount < -abs(looking_wallet.credit_limit):
                            wallet_remove_amount = looking_wallet_amount + abs(looking_wallet.credit_limit)

                        wallet_dict_available[looking_wallet] = wallet_dict_available[
                                                                    looking_wallet] - wallet_remove_amount
                        amount = amount - wallet_remove_amount

                        wallet_amount_to_apply[looking_wallet] = wallet_amount_to_apply[
                                                                     looking_wallet] + wallet_remove_amount

                if looking_wallet == self.env.company.default_wallet_category_id:
                    break
                looking_wallet = wallet_id.get_wallet_by_category_id(looking_wallet.category_id.parent_id)
        return dict(wallet_amount_to_apply)

    def get_wallet_partner(self):
        """ This is used to be inherited by school_walllet module """
        self.ensure_one()
        return self.partner_id
