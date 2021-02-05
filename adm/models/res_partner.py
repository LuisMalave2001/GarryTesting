'''
Created on Feb 1, 2020

@author: LuisMora
'''
from odoo import models, fields


class ResPartnerExtended(models.Model):
    _inherit = ["res.partner"]

    application_id = fields.Many2one("adm.application", string="Application")

    inquiry_id = fields.Many2one("adm.inquiry", string="Inquiry")
    is_in_application = fields.Boolean("Is in Application?")
    application_sibling_ids = fields.Many2many("adm.application")

    date_of_birth = fields.Date("date_of_birth")
    gender = fields.Many2one("adm.gender", string="Gender")

    school_grade = fields.Char("School grade")
    school = fields.Char("Current school")

    # relationship_ids = fields.One2many("adm.relationship", "partner_1", string="Relationships")
    house_address_ids = fields.One2many("adm.house_address", "family_id", string="House Addresses")

    medical_allergies_ids = fields.One2many("adm.medical_allergy", "partner_id", string="Medical Allergies")
    medical_conditions_ids = fields.One2many("adm.medical_condition", "partner_id", string="Medical conditions")
    medical_medications_ids = fields.One2many("adm.medical_medication", "partner_id", string="Medical Medication")

    house_address_id = fields.Many2one("adm.house_address", string="Home Address")
    citizenship = fields.Many2one("res.country", string="Citizenship")
    identification = fields.Char("Identification")
    marital_status = fields.Selection(
        [("married", "Married"),
         ("single", "Single"),
         ("divorced", "Divorced"),
         ("widowed", "Widowed")],
        string="Marital Status")
    occupation = fields.Char("Occupation")
    parental_responsability = fields.Boolean("Parental Responsability")
    title = fields.Char("Title")
    work_address = fields.Char("Office Address")

    work_phone = fields.Char("Office Phone")
    home_phone = fields.Char("Home Phone")

    work_email = fields.Char('Work email')

    # Education information
    education = fields.Char()
    school_name = fields.Char()
    degree = fields.Char()
    first_language = fields.Char()
