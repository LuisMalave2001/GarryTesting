# -*- coding: utf-8 -*-

from odoo import fields, models, api

class AccountJournal(models.Model):
    _inherit = "account.journal"

    check_template_id = fields.Many2one(string="Check Template",
        comodel_name="ir.ui.view",
        domain=[("type","=","qweb")])