# -*- coding: utf-8 -*-

from dateutil import parser
from pytz import timezone, utc

from odoo import models, fields, api
from odoo.tools import format_duration

class ResPartnerReportStatement(models.AbstractModel):
    _name = "report.school_statement_report.res_partner_report_statement"
    _description = "Partner Statment Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        partner_obj = self.env["res.partner"]
        move_line_obj = self.env["account.move.line"]
        partners = partner_obj.browse(docids)
        data = {}
        for partner in partners:
            move_lines = move_line_obj.search([
                ("partner_id","=",partner.id),
                ("move_id.state","=","posted"),
                ("full_reconcile_id","=",False),
                ("balance","!=",0),
                ("account_id.reconcile","=",True),
                ("display_type","not in",("line_section","line_note")),
            ], order="date asc")
            students = []
            for line in move_lines:
                if line.student_id not in students:
                    students.append(line.student_id)
            data[partner] = {
                "lines": move_lines,
                "students": students,
            }
        return {
            "doc_ids": docids,
            "doc_model": "res.partner",
            "docs": partners,
            "data": data,
        }