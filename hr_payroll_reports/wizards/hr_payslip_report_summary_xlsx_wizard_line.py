# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrPayslipXlsxReportSummaryXlsxWizardLine(models.TransientModel):
    _name = "hr.payslip.report.summary.xlsx.wizard.line"
    _description = "Payslip Summary Report Wizard Line"
    _order = "sequence, id"

    wizard_id = fields.Many2one(string="Wizard",
        comodel_name="hr.payslip.report.summary.xlsx.wizard",
        required=True,
        ondelete="cascade")
    name = fields.Char(string="Header")
    type = fields.Selection(string="Type",
        selection=[
            ("field", "Field"),
            ("rule", "Rule"),
            ("total", "Total")],
        required=True)
    field_id = fields.Many2one(string="Field",
        comodel_name="ir.model.fields")
    rule_id = fields.Many2one(string="Rule",
        comodel_name="hr.salary.rule")
    code = fields.Char(string="Code",
        related="rule_id.code")
    struct_id = fields.Many2one(string="Structure",
        comodel_name="hr.payroll.structure",
        related="rule_id.struct_id")
    sequence = fields.Integer(string="Sequence",
        default=500)