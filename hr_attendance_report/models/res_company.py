# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    overtime_start = fields.Float(string="Overtime Start (Hours)",
        default=10,
        help="Used in attendance reporting to determine when to count worked hours as overtime.")