# """
# Created on Feb 1, 2020
#
# @author: LuisMora
# """
#
# from odoo import models, fields, _, api
#
#
# class Relationship(models.Model):
#     _name = 'adm.relationship'
#     _description = "Adm relationship"
#
#     partner_1 = fields.Many2one("res.partner", string="Partner 1", required=True, ondelete="cascade")
#     partner_2 = fields.Many2one("res.partner", string="Partner", required=True, ondelete="cascade")
#
#     partner_2_email = fields.Char(related="partner_2.email")
#     name = fields.Char(related='partner_2.name')
#     image = fields.Binary("Applicant´s Photo", related="partner_2.image_1920")
#
#     relationship_type = fields.Selection(
#         [('sibling', "Sibling"), ('father', "Father"), ('mother', "Mother"), ('uncle', "Uncle"), ('grandmother', "Grandmother"), ('grandfather', "Grandfather"),
#          ('other', "Other"), ], string="Type", default='other')
#
#     custody = fields.Boolean(string="Custiodial rights")
#
#     financial_responsability = fields.Boolean()
#     is_emergency_contact = fields.Boolean("Is an emergency contact?")
#     residency_permit_id_number = fields.Many2one('ir.attachment')
#     parent_passport_upload = fields.Many2one('ir.attachment')
#
#     @api.model
#     def create(self, values):
#         relationship = super(Relationship, self).create(values)
#         relationship.update_partner_2_family()
#         return relationship
#
#     def write(self, values):
#         success = super(Relationship, self).write(values)
#         if success:
#             self.update_partner_2_family()
#         return success
#
#     def update_partner_2_family(self):
#         for relationship in self:
#             for family in relationship.partner_1.family_ids:
#                 if relationship.partner_2:
#                     relationship.partner_2.write({
#                         'family_ids': [(4, family.id, False)]
#                         })
#
#                     family.write({
#                         'member_ids': [(4, relationship.partner_2.id, False)]
#                         })
#                     if relationship.relationship_type in ['father', 'mother']:
#                         relationship.partner_2.person_type = 'parent'
