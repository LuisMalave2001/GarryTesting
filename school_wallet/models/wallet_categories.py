from odoo import fields, models, api
from odoo.tools import float_round


class WalletCategory(models.Model):
    _inherit = 'wallet.category'

    def _get_related_partner_wallet_moves_domain(self, partner_id):
        if partner_id.person_type == 'student':
            return [('student_id', '=', partner_id.id), ('state', '=', 'posted'), ]
        else:
            return super(WalletCategory, self)._get_related_partner_wallet_moves_domain(partner_id)
