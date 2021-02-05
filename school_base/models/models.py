# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# from odoo.addons.school_base.models.res_partner import SELECT_STATUS_TYPES


class SchoolCode(models.Model):
    _name = "school_base.school_code"
    _order = "sequence"
    _description = "School code"

    name = fields.Char(string="code", required=True)
    school_name = fields.Char(string="School name")
    sequence = fields.Integer(default=1)
    district_code_id = fields.Many2one("school_base.district_code", "District Code")


class SchoolYear(models.Model):
    _name = "school_base.school_year"
    _order = "sequence"
    _description = "School year"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    facts_id = fields.Integer("Facts ID", readonly=True)
    active_admissions = fields.Boolean('Active admissions')
    school_code_id = fields.Many2one("school_base.school_code", string="School code")
    district_code_id = fields.Many2one(related="school_code_id.district_code_id")

    @api.onchange('school_code_id')
    def _get_school_code_id_domain(self):
        self.ensure_one()
        school_code_ids = self.district_code_id.school_code_ids.ids
        return {'domain': {'school_code_id': [('id', 'in', school_code_ids)]}}


class GradeLevel(models.Model):
    _name = "school_base.grade_level"
    _order = "sequence"
    _description = "The grade level"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    school_code_id = fields.Many2one("school_base.school_code", string="School code")
    district_code_id = fields.Many2one(related="school_code_id.district_code_id")
    user_type_id = fields.Many2one('school_base.grade_level.type')
    capacity = fields.Integer()

    @api.onchange('school_code_id')
    def _get_school_code_id_domain(self):
        self.ensure_one()
        school_code_ids = self.district_code_id.school_code_ids.ids
        return {'domain': {'school_code_id': [('id', 'in', school_code_ids)]}}


class SchoolBaseGradeLevelType(models.Model):
    _name = 'school_base.grade_level.type'
    _description = "Grade level type"

    type = fields.Selection(
        [
            ('elementary', _("Elementary")),
            ('middle_school', _("Middle school")),
            ('high_school', _("High school")),
            ],
            required=True
        )
    name = fields.Char(required=True)


class DistrictCode(models.Model):
    """ District code """
    _name = "school_base.district_code"
    _description = "District code"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    school_code_ids = fields.One2many("school_base.school_code", "district_code_id", string="School code")


class Placement(models.Model):
    """ An informative model for students """
    _name = 'school_base.placement'
    _description = "Placement"
    name = fields.Char(string="Placement", required=True, translate=True)
    key = fields.Char(string="Key")


class WithdrawReason(models.Model):
    """ Why does the student withdraw? """
    _name = 'school_base.withdraw_reason'
    _description = "Withdraw reasons"
    name = fields.Char(string="WithDraw Reason", required=True, translate=True)
    key = fields.Char(string="Key")


class Status(models.Model):
    """ SubStatus for students """
    _name = 'school_base.enrollment.status'
    _description = "Enrollment Status"
    # status_id = fields.Selection(SELECT_STATUS_TYPES, string='Status')
    name = fields.Char(string="Name", required=True, translate=True)
    key = fields.Char(string="Key")
    note = fields.Char(string="Description")


class SubStatus(models.Model):
    """ SubStatus for students """
    _name = 'school_base.enrollment.sub_status'
    _description = "Enrollment sub status"

    # status_id = fields.Selection(SELECT_STATUS_TYPES, string='Status')
    status_id = fields.Selection([('1', '1')], string='Status')
    name = fields.Char(string="Name", required=True, translate=True)
    key = fields.Char(string="Key")


class MaritalStatus(models.Model):
    """ An informative model for students """
    _name = 'school_base.marital_status'
    _description = "Marital Status"
    name = fields.Char(string="Name", required=True, translate=True)
    key = fields.Char(string="Key")


class Gender(models.Model):
    _name = "school_base.gender"
    name = fields.Char("Gender", required=True, translate=True)
    key = fields.Char("Key")
