# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_wallet_partner(self):
        self.ensure_one()
        if self.student_id:
            return self.student_id
        else:
            if self.family_id:
                return self.family_id
            else:
                return super(AccountMove, self).get_wallet_partner()

    def get_wallet_credit_note_values(self, partner_id, journal_id,
                                      invoice_line_ids):
        values = super(AccountMove, self).get_wallet_credit_note_values(
            partner_id, journal_id, invoice_line_ids)
        values.update({
            'family_id': self.family_id.id,
            'student_id': self.student_id.id,
            })
        return values
