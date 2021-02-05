# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, MissingError

class ResPartner(models.Model):
    _inherit = "res.partner"

    tuition_plan_ids = fields.Many2many(string="Tuition Plans",
        comodel_name="tuition.plan",
        relation="partner_tuition_plan_rel",
        help="""Tuition plans that were manually assigned to the student.
            If a plan in the Default Tuition Plan overlaps with any of these,
            then the overlapping default tuition plan will be removed""",
        domain="[('grade_level_ids','in',[grade_level_id])]")
    default_tuition_plan_ids = fields.Many2many(string="Default Tuition Plans",
        comodel_name="tuition.plan",
        compute="_compute_default_tuition_plan_ids",
        help="Tuition plans used if no tuition plan is manually set for a given school year, category, and gradelevel")
    email_statement = fields.Boolean(string="Email Statement Report")
    
    def _compute_default_tuition_plan_ids(self):
        for partner in self:
            result = []
            if partner.grade_level_id and partner.person_type == "student":
                default_plans = self.env["tuition.plan"].search([("default","=",True),])
                for plan in default_plans:
                    if partner.id in plan.default_partner_ids.ids:
                        result.append(plan.id)
            partner.default_tuition_plan_ids = result

    @api.constrains("tuition_plan_ids")
    def _check_tuition_plan_ids(self):
        for partner in self:
            for plan in partner.tuition_plan_ids:
                overlapping = plan.get_overlapping_plans()
                intersection = overlapping & (partner.tuition_plan_ids - plan)
                if intersection:
                    raise ValidationError("The plan %s overlaps with %s for student %s." %
                        (plan.name, ", ".join(intersection.mapped("name")), partner.name))