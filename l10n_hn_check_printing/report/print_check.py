# -*- coding: utf-8 -*-

from odoo import models
from odoo.tools.misc import format_date, formatLang

from ..tools import tools

class report_print_check(models.Model):
    _inherit = 'account.payment'

    def _check_build_page_info(self, i, p):
        number_converter = tools.NumberToTextConverter("LP.", "LPS.", "CTV.", "CTVS.")
        page = super(report_print_check, self)._check_build_page_info(i, p)
        page.update({
            'date_label': self.company_id.account_check_printing_date_label,
            'payment_date_honduras': format_date(self.env, self.payment_date, date_format='dd-MM-yyyy'),
            'amount': formatLang(self.env, self.amount) if i == 0 else 'VOID',
            'amount_in_word': number_converter.numero_a_letra(self.amount) if i == 0 else 'VOID',
            'company': self.company_id,
            'move_lines': self.move_line_ids,
            'sequence_number': self.check_number,
        })
        return page
