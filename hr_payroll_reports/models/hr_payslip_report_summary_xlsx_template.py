# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class HrPayslipXlsxReportSummaryXlsxTemplate(models.Model):
    _name = "hr.payslip.report.summary.xlsx.template"
    _description = "Payslip Summary Report Template"

    name = fields.Char(string="Name",
        required=True)
    grouping = fields.Selection(string="Group By",
        selection=[ 
            ('department', 'Department')],
        default='department')
    line_ids = fields.One2many(string="Lines",
        comodel_name="hr.payslip.report.summary.xlsx.template.line",
        inverse_name="template_id")