# -*- coding: utf-8 -*-
from odoo import models, fields


class AdmissionDegreeProgram(models.Model):
    _name = 'adm.degree_program'
    _description = "Adm Degree program"

    name = fields.Char("Name")
