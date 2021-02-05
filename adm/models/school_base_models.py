# -*- coding: utf-8 -*-

from odoo import models, fields


class SchoolBaseSchoolYear(models.Model):
    _inherit = 'school_base.school_year'

    active_admissions = fields.Boolean()


class SchoolBaseGradeLevel(models.Model):
    _inherit = 'school_base.grade_level'

    active_admissions = fields.Boolean()
