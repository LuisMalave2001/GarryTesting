# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def open_student_ledger(self):
        return {
            'type': 'ir.actions.client',
            'name': _('Student Ledger'),
            'tag': 'account_report',
            'options': {'partner_ids': [self.id]},
            'ignore_session': 'both',
            'context': "{'model':'account.student.ledger'}"
        }
    
    def open_family_ledger(self):
        return {
            'type': 'ir.actions.client',
            'name': _('Family Ledger'),
            'tag': 'account_report',
            'options': {'family_ids': [self.id]},
            'ignore_session': 'both',
            'context': "{'model':'account.student.ledger'}"
        }
