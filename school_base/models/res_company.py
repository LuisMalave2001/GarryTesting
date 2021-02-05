# -*- encoding: utf-8 -*-

from ..utils import formatting

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    district_code_id = fields.Many2one("school_base.district_code", "District code")
    school_code_id = fields.Many2one('school_base.school_code', string="School code")
    district_code_name = fields.Char(related="district_code_id.name")
    date_sincro_contacts = fields.Datetime(help="Used to know the last time that was synchronized")
    school_year_id = fields.Many2one('school_base.school_year', string="Current School Year")
