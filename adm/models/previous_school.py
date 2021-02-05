'''
Created on Feb 14, 2020

@author: LuisMora
'''

from odoo import fields, models


class PreviousSchoolDescription(models.Model):
    _name = 'adm.previous_school_description'
    _description = "Adm Previous school description"

    application_id = fields.Many2one("adm.application")

    name = fields.Char("Name")
    street = fields.Char("Street")
    city = fields.Char("City")
    zip = fields.Char("ZIP")
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    grade_completed = fields.Char("Grade Current or Completed")
    extracurricular_interests = fields.Char(
        "Applicant’s extracurricular interests")
    reason_for_leaving = fields.Char()
