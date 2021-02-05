# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    canteen_ok = fields.Boolean(string="Can be Sold in Canteen")
    canteen_recur_monday = fields.Boolean(string="Available on Mondays")
    canteen_recur_tuesday = fields.Boolean(string="Available on Tuesdays")
    canteen_recur_wednesday = fields.Boolean(string="Available on Wednesdays")
    canteen_recur_thursday = fields.Boolean(string="Available on Thursdays")
    canteen_recur_friday = fields.Boolean(string="Available on Fridays")
    canteen_recur_saturday = fields.Boolean(string="Available on Saturdays")
    canteen_recur_sunday = fields.Boolean(string="Available on Sundays")
    canteen_availability_dates = fields.Many2many(string="Canteen Availability",
        comodel_name="canteen.availability")