# -*- coding: utf-8 -*-
from odoo import models, fields, _, api, exceptions


class Allergy(models.Model):
    _name = "school_base.allergy"
    _description = "Allergies for contacts (students or somebody else)"

    name = fields.Char("Name")
    description = fields.Char("Description")
    partner_id = fields.Many2one("res.partner", "Contact")
    facts_id = fields.Integer('Facts Id')

    @api.constrains('facts_id')
    def check_unique_facts_id(self):
        for allergy in self:
            if allergy.facts_id and allergy.search_count([('facts_id', '=', allergy.facts_id)]) > 1:
                raise exceptions.ValidationError(_('There exists an codition with the same facts id [%s]' % allergy.facts_id))
