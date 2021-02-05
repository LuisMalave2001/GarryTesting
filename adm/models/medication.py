"""
Created on Feb 18, 2020

@author: LuisMora
"""

from odoo import models, fields


class MedicalCondition(models.Model):
    _name = 'adm.medical_medication'
    _description = "Adm Medical medication"

    name = fields.Char("Name")
    comment = fields.Char("Comment")

    partner_id = fields.Many2one("res.partner", string="Partner")
