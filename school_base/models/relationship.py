"""
Created on Feb 1, 2020

@author: LuisMora
"""
from odoo import models, fields, api, _


class Relationship(models.Model):
    _name = "school_base.relationship"

    partner_1 = fields.Many2one("res.partner", string="Partner 1", required=True, ondelete="cascade")
    partner_2 = fields.Many2one("res.partner", string="Partner", required=True, ondelete="cascade")
    family_id = fields.Many2one("res.partner", string="Family", required=True, domain=[('is_family', '=', True)])
    relationship_type_id = fields.Many2one("school_base.relationship_type", string="Relationship")
    custody = fields.Boolean(string="Custody")
    correspondence = fields.Boolean(string="Correspondence")
    grand_parent = fields.Boolean(string="Grand Parent")
    grade_related = fields.Boolean(string="Grade Related")
    family_portal = fields.Boolean(string="Family Portal")
    is_emergency_contact = fields.Boolean("Is an emergency contact?")

    financial_responsability = fields.Boolean()
    residency_permit_id_number = fields.Many2one('ir.attachment')
    parent_passport_upload = fields.Many2one('ir.attachment')

    @api.model
    def create(self, values):
        relationship = super(Relationship, self).create(values)
        relationship.update_partner_2_family()
        return relationship

    def write(self, values):
        success = super(Relationship, self).write(values)
        if success:
            self.update_partner_2_family()
        return success

    def update_partner_2_family(self):
        for relationship in self:
            for family in relationship.partner_1.family_ids:
                if relationship.partner_2:
                    relationship.partner_2.write({
                        'family_ids': [(4, family.id, False)]
                        })

                    family.write({
                        'member_ids': [(4, relationship.partner_2.id, False)]
                        })
                    if relationship.relationship_type_id.key in ['father', 'mother']:
                        relationship.partner_2.person_type = 'parent'
    # relationship_type = fields.Selection([
    #         ('sibling', "Sibling"),
    #         ('father', "Father"),
    #         ('mother', "Mother"),
    #         ('uncle', "Uncle"),
    #         ('grandmother', "Grandmother"),
    #         ('grandfather', "Grandfather"),
    #         ('other', "Other"),
    #     ],
    #     string="Type", default='other'
    # )


class RelationshipType(models.Model):
    """ SubStatus for students """
    _name = 'school_base.relationship_type'
    _description = "Relationship Type"
    _order = "sequence"

    name = fields.Char(string="Relationship type", required=True, translate=True)
    key = fields.Selection([
        ('sibling', _("Sibling")),
        ('father', _("Father")),
        ('mother', _("Mother")),
        ('grandmother', _("Grand mother")),
        ('grandfather', _("Grand father")),
        ('stepmother', _("Step mother")),
        ('stepfather', _("Step father")),
        ('stepsibling', _("Step sibling")),
        ], string="Key")
    sequence = fields.Integer(default=1)
