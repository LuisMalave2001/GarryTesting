'''
Created on Feb 18, 2020

@author: LuisMora
'''
from odoo import models, fields


class MedicalAllergy(models.Model):
    _name = "school_base.medical_allergy"

    name = fields.Char("Name")
    comment = fields.Char("Comment")

    partner_id = fields.Many2one("res.partner", string="Partner")


