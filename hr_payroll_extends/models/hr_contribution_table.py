#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrContributionTable(models.Model):
    _name = "hr.contribution.table"
    _description = "Contribution Table"

    name = fields.Char(string="Name",
        required=True)
    bracket_ids = fields.One2many(string="Brackets",
        comodel_name="hr.contribution.bracket",
        inverse_name="table_id")