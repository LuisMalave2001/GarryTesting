# -*- coding: utf-8 -*-

from odoo import models, api


class AccountBankStmtCashWizard(models.Model):
    """ Modified to pass paymeth_method_id and computed_amount to the new lines """
    _inherit = 'account.bank.statement.cashbox'

    @api.model
    def default_get(self, fields):
        """ Pass payment_method and computed_amount to the new lines """
        vals = super().default_get(fields)

        if "cashbox_lines_ids" in vals:
            config_id = self.env.context.get('default_pos_id')
            if config_id:
                config = self.env['pos.config'].browse(config_id)
                if config.last_session_closing_cashbox.cashbox_lines_ids:
                    lines = config.last_session_closing_cashbox.cashbox_lines_ids
                else:
                    lines = config.default_cashbox_id.cashbox_lines_ids

                if lines:
                    cashbox_lines_ids = vals["cashbox_lines_ids"]
                    DICT_POS = 2
                    for i, line in enumerate(lines):
                        cashbox_lines_ids[i][DICT_POS]["payment_method_id"] = line.payment_method_id.id
                        cashbox_lines_ids[i][DICT_POS]["currency_id"] = line.currency_id.id
        return vals
