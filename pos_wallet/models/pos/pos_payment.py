from odoo import api, fields, models, _
from odoo.tools import formatLang
from odoo.exceptions import ValidationError


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    # Add wallet payment to the formula :P
    @api.constrains('payment_method_id')
    def _check_payment_method_id(self):
        for payment in self:
            # The condition is (A and B) or (not A and C)
            # This can be simplified to B if A else C
            # The idea is check A only once

            if payment.payment_method_id not in payment.session_id.config_id.wallet_category_ids.mapped('pos_payment_method_id') \
                    if payment.payment_method_id.is_wallet_payment_method \
                    else payment.payment_method_id not in payment.session_id.config_id.payment_method_ids:
                raise ValidationError(_('The payment method selected is not allowed in the config of the POS session.'))
