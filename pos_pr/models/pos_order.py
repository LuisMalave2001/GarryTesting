# -*- coding: utf-8 -*-

from odoo import models, fields, _


class PosOrder(models.Model):
    """ Added some functionalities to help us """
    _inherit = "pos.order"

    def get_receivable_account(self):
        """ To allow modifying this property I encapsulate it in this function """
        self.ensure_one()
        return self.partner_id.property_account_receivable_id
