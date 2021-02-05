# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class Condition(models.Model):
    _name = "school_base.condition"
    _description = "Conditions for contacts (students or somebody else)"

    name = fields.Char("Name")
    description = fields.Char("Description")
    partner_id = fields.Many2one("res.partner", "Contact")
    facts_id = fields.Integer('Facts Id')

    @api.constrains('facts_id')
    def check_unique_facts_id(self):
        for condition in self:
            if condition.facts_id and condition.search_count([('facts_id', '=', condition.facts_id)]) > 1:
                raise exceptions.ValidationError(_('There exists an codition with the same facts id [%s]' % condition.facts_id))
