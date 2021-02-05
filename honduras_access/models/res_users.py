# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        if not self.env.user.has_group("base.group_system") and self.env.user.has_group("honduras_access.group_academic_secretary"):
            self = self.sudo()
        return super(ResUsers, self).create(vals)
