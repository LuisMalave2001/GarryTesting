# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployeeReportAttendanceWizard(models.TransientModel):
    _name = "hr.employee.report.attendance.wizard"

    start_date = fields.Date(string="Start Date",
        required=True)
    end_date = fields.Date(string="End Date",
        required=True)
    duration_format = fields.Selection(string="Duration Format",
        selection=[
            ("sexagesimal", "Sexagesimal (HH:MM)"),
            ("decimal", "Decimal (H.M)")],
        required=True,
        default="sexagesimal")

    def action_confirm(self):
        active_ids = self.env.context.get("active_ids", [])
        datas = {
            "ids": active_ids,
            "model": "hr.employee",
            "form": self.read()[0]
        }

        return self.env.ref("hr_attendance_report.action_hr_employee_report_attendance").report_action([], data=datas)