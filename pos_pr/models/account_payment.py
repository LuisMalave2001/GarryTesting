# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    """ Added some functionalities to payment and add some group """
    _inherit = "account.payment"

    def get_receivable_line(self):
        """ Return the receivable line """
        self.ensure_one()
        move_line = self.mapped("move_line_ids").filtered(lambda move_line: move_line.account_id.user_type_id.type == 'receivable')
        if move_line:
            move_line.ensure_one()

        return move_line

    def get_receivable_account(self):
        """ Return the receivable account """
        self.ensure_one()
        move_line = self.mapped("move_line_ids").filtered(
            lambda move_line: move_line.account_id.user_type_id.type == 'receivable')
        return move_line.account_id

