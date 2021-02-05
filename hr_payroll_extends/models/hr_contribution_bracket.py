#-*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang

class HrContributionBracket(models.Model):
    _name = "hr.contribution.bracket"
    _description = "Contribution Bracket"
    _order = "lower_limit"

    table_id = fields.Many2one(string="Table",
        comodel_name="hr.contribution.table",
        required=True,
        ondelete="cascade")
    next_bracket_id = fields.Many2one(string="Next Bracket",
        comodel_name="hr.contribution.bracket",
        compute="_compute_next_bracket_id")
    lower_limit = fields.Float(string="Lower Limit (Exclusive)")
    upper_limit_text = fields.Char(string="Upper Limit (Inclusive)",
        compute="_compute_upper_limit_text")
    fixed_amount = fields.Float(string="Fixed Amount")
    percentage_amount = fields.Float(string="Percentage Amount")
    rate_text = fields.Char(string="Rate of Tax",
        compute="_compute_rate_text")

    def _compute_next_bracket_id(self):
        for bracket in self:
            next_bracket_id = False
            bracket_ids = bracket.table_id.bracket_ids.ids
            if bracket_ids:
                curr_index = bracket_ids.index(bracket.id)
                if curr_index < (len(bracket_ids) - 1):
                    next_bracket_id = bracket_ids[curr_index + 1]
            bracket.next_bracket_id = next_bracket_id
    
    def _compute_upper_limit_text(self):
        for bracket in self:
            lower_limit = bracket.next_bracket_id.lower_limit
            bracket.upper_limit_text = lower_limit and _("to %s") % formatLang(self.env, lower_limit) or _("and above")

    def _compute_rate_text(self):
        for bracket in self:
            bracket.rate_text = _("%s plus %d%% of the amount exceeding %s") % \
                (formatLang(self.env, bracket.fixed_amount), bracket.percentage_amount, formatLang(self.env, bracket.lower_limit))