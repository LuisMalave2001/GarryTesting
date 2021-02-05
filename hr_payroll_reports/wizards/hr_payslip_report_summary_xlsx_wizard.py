# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

DEFAULT_FIELDS = [
    "hr.field_hr_employee__name",
    "hr.field_hr_employee__job_id",
]

class HrPayslipXlsxReportSummaryXlsxWizard(models.TransientModel):
    _name = "hr.payslip.report.summary.xlsx.wizard"
    _description = "Payslip Summary Report Wizard"

    def _default_struct_ids(self):
        active_ids = self.env.context.get("active_ids", [])
        payslips = self.env["hr.payslip"].browse(active_ids)
        return payslips.mapped("struct_id").ids
    
    def _default_line_ids(self):
        res = []
        for index, field in enumerate(DEFAULT_FIELDS):
            res.append((0, 0, {
                "sequence": index,
                "type": "field",
                "field_id": self.env.ref(field)
            }))
        struct_ids = self._default_struct_ids()
        sequence = len(DEFAULT_FIELDS)
        for struct_id in struct_ids:
            struct = self.env["hr.payroll.structure"].browse(struct_id)
            for rule in struct.rule_ids:
                res.append((0, 0, {
                    "sequence": sequence,
                    "type": "rule",
                    "rule_id": rule.id,
                    "code": rule.code,
                    "struct_id": rule.struct_id.id,
                }))
                sequence += 1
        return res

    grouping = fields.Selection(string="Group By",
        selection=[ 
            ('department', 'Department')],
        default='department')
    line_ids = fields.One2many(string="Lines",
        comodel_name="hr.payslip.report.summary.xlsx.wizard.line",
        inverse_name="wizard_id")
    struct_ids = fields.Many2many(string="Salary Structures",
        comodel_name="hr.payroll.structure",
        default=_default_struct_ids,
        readonly=True)
    template_id = fields.Many2one(string="Template",
        comodel_name="hr.payslip.report.summary.xlsx.template")
    template_name = fields.Char(string="Save as Template")

    @api.onchange("template_id")
    def _onchange_template_id(self):
        self.ensure_one()
        result = []
        self.line_ids = [(5, 0)]
        if self.template_id:
            self.grouping = self.template_id.grouping
            for index, line in enumerate(self.template_id.line_ids):
                result.append((0, 0, {
                    "sequence": line.sequence,
                    "type": line.type,
                    "field_id": line.field_id.id,
                    "rule_id": line.rule_id.id,
                    "code": line.code,
                    "struct_id": line.rule_id.struct_id.id,
                    "name": line.name,
                }))
        self.line_ids = result or self._default_line_ids()
    
    def action_save_as_template(self):
        self.ensure_one()
        if not self.template_name:
            raise UserError("Please provide a name for the template.")
        if not self.line_ids:
            raise UserError("Please add columns before saving as a template.")

        line_ids = []
        for line in self.line_ids:
            line_ids.append((0, 0, {
                "sequence": line.sequence,
                "type": line.type,
                "field_id": line.field_id.id,
                "rule_id": line.rule_id.id,
                "code": line.code,
                "struct_id": line.rule_id.struct_id.id,
                "name": line.name,
            }))
        template = self.env["hr.payslip.report.summary.xlsx.template"].create({
            "name": self.template_name,
            "grouping": self.grouping,
            "line_ids": line_ids
        })
        return {"type": "ir.actions.do_nothing"}

    def action_confirm(self):
        active_ids = self.env.context.get("active_ids", [])
        datas = {
            "ids": active_ids,
            "model": "hr.payslip",
            "form": self.read()[0]
        }
        return self.env.ref("hr_payroll_reports.action_hr_payslip_report_summary_xlsx").report_action([], data=datas)