# -*- coding: utf-8 -*-
from odoo import models, fields

class AdmissionPreferredContactTime(models.Model):
    _name = 'adm.contact_time'
    _description = "Adm contact time"
    
    name = fields.Char("Name", required=True)
    from_time = fields.Float("From Time", required=True)
    to_time = fields.Float("To Time", required=True)