'''
Created on Feb 18, 2020

@author: LuisMora
'''
from odoo import models, fields

class MedicalCondition(models.Model):
    _name = "school_base.medical_medication"
    
    name = fields.Char("Name")
    comment = fields.Char("Comment")
    
    partner_id = fields.Many2one("res.partner", string="Partner")