# -*- coding: utf-8 -*-

from dateutil import parser
from pytz import timezone, utc

from odoo import models, fields, api
from odoo.tools import format_duration

class HrEmployeeReportAttendance(models.AbstractModel):
    _name = "report.hr_attendance_report.hr_employee_report_attendance"

    @api.model
    def _get_report_values(self, docids, data=None):
        employee_ids = self.env.context.get("active_ids", [])
        employees = self.env["hr.employee"].browse(employee_ids)
        start_date = parser.parse(data["form"]["start_date"])
        end_date = parser.parse(data["form"]["end_date"])
        tz = timezone(self.env.user.tz or "UTC")
        attendances = {}
        for employee in employees:
            utc_datetime = utc.localize(start_date)
            start_time = utc_datetime.astimezone(tz)
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)

            utc_datetime = utc.localize(end_date)
            end_time = utc_datetime.astimezone(tz)
            end_time = end_time.replace(hour=23, minute=59, second=59, microsecond=999)

            start_utc = start_time.astimezone(utc)
            end_utc = end_time.astimezone(utc)

            attendances[employee.id] = self.env["hr.attendance"].search([
                ("employee_id","=",employee.id),
                ("check_in",">=", start_utc),
                ("check_in","<=", end_utc)
            ]).sorted(key=(lambda a: (a.check_in, a.id)))

        return {
            "doc_ids": employee_ids,
            "doc_model": "hr.employee",
            "docs": employees,
            "data": data,
            "attendances": attendances,
            "format_duration": format_duration,
            "duration_format": data["form"]["duration_format"],
        }