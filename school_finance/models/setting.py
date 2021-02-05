# -*- coding: utf-8 -*-

from odoo import models, fields, _

receivable_behaviour_selection = [
    ("default", "Default"),
    ("student", "Student"),
]

class SchoolFinanceSettings(models.TransientModel):
    _inherit = "res.config.settings"

    receivable_behaviour = fields.Selection(receivable_behaviour_selection,
                            string='Receivable Behaviour',
                            config_parameter='school_finance.receivable_behaviour',
                            default="default")
