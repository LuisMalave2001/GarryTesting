# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CanteenAvailability(models.Model):
    _name = "canteen.availability"
    _description = "Canteen Availability"
    _rec_name = "date"

    date = fields.Date(string="Date",
        required=True)
    
    _sql_constraints = [
        ("date_uniq", "unique (date)", "This date already exists"),
    ]