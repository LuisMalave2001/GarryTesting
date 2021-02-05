#-*- coding: utf-8 -*-

from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = "res.groups"

    def get_members_email_to(self):
        self.ensure_one()
        return ",".join(self.users.filtered(lambda u: u.email).mapped("email"))

