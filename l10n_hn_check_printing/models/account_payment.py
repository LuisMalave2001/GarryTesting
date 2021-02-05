# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError

class account_payment(models.Model):
    _inherit = "account.payment"

    def do_print_checks(self):
        if self:
            check_layout = self[0].company_id.account_check_printing_layout
            if check_layout != 'disabled' and self[0].journal_id.company_id.country_id.code == 'HN':
                if self[0].journal_id.check_template_id:
                    self.write({'state': 'sent'})
                    return self.env.ref('l10n_hn_check_printing.action_print_check').report_action(self)
                else:
                    raise UserError(_("You have to choose a check layout. For this, go to the journal settings and set one."))
        return super(account_payment, self).do_print_checks()
