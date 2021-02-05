# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    student_id = fields.Many2one("res.partner", "Student", readonly=True)
    student_grade_level = fields.Many2one("school_base.grade_level", "Grade Level", readonly=True)
    student_homeroom = fields.Char("Homeroom", readonly=True)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + \
            ", move.student_id as student_id, move.student_grade_level as student_grade_level, move.student_homeroom as student_homeroom"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + \
            ", move.student_id, move.student_grade_level, move.student_homeroom"