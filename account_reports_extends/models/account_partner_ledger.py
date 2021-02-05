# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"

    @api.model
    def _get_query_amls(self, options, expanded_partner=None, offset=None, limit=None):
        query, where_params = super(AccountPartnerLedger, self)._get_query_amls(options, expanded_partner, offset, limit)
        query = query.replace("ORDER BY account_move_line.id", "ORDER BY account_move_line.date, account_move_line.id")
        return query, where_params