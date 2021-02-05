# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    overtime_start = fields.Float(string="Overtime Start (Hours)",
        related="company_id.overtime_start",
        help="Used in attendance reporting to determine when to count worked hours as overtime.",
        readonly=False)