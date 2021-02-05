# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Service(models.Model):
    _name = "school_base.service"
    _description = "School Service"

    name = fields.Char(string="Name")