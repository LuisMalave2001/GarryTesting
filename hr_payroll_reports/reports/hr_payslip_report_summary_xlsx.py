# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrPayslipReportSummaryXlsx(models.AbstractModel):
    _name = "report.hr_payroll_reports.hr_payslip_report_summary_xlsx"
    _description = "Payslip Summary Report"
    _inherit = "report.report_xlsx.abstract"

    def _get_column_header(self, column):
        header = ""
        if column.name:
            header = column.name
        elif column.type == "field":
            header = column.field_id.field_description
        elif column.type == "rule":
            header = column.rule_id.name
        elif column.type == "total":
            header = "Total"
        return header

    def _generate_lines(self, sheet, columns, payslips, offset, styles, grand_totals, title=None):
        if title:
            sheet.write(offset, 0, title, styles["section_style"])
            sheet.set_row(offset, 21)
            offset += 1

        sheet.write(offset, 0, "#", styles["header_bold_style"])
        for c_index, column in enumerate(columns):
            header = self._get_column_header(column)
            sheet.write(offset, c_index + 1, header, styles["header_bold_style"])
            sheet.set_column(1, c_index + 1, 30)
        offset += 1

        totals = {}
        for p_index, payslip in enumerate(payslips):
            sheet.write(offset, 0, p_index + 1)
            total = 0
            for c_index, column in enumerate(columns):
                value = None
                style = styles["base_style"]
                skip_write = False
                if column.type == "field":
                    source = payslip
                    if column.field_id.model_id.model == "hr.employee":
                        source = payslip.employee_id
                    elif column.field_id.model_id.model == "hr.contract":
                        source = payslip.contract_id

                    if column.field_id.ttype == "many2one":
                        value = getattr(source, column.field_id.name).display_name
                    elif column.field_id.ttype in ["one2many", "many2many"]:
                        value = ", ".join(getattr(source, column.field_id.name).mapped("display_name"))
                    else:
                        value = getattr(source, column.field_id.name)
                        if value:
                            if column.field_id.ttype == "date":
                                style = styles["date_style"]
                            elif column.field_id.ttype == "datetime":
                                style = styles["datetime_style"]
                elif column.type == "rule":
                    value = 0
                    style = styles["number_style"]
                    totals.setdefault(column.id, 0)
                    grand_totals.setdefault(column.id, 0)
                    for line in payslip.line_ids:
                        if line.salary_rule_id == column.rule_id:
                            value = abs(line.total)
                            total += value
                            totals[column.id] += value
                            grand_totals[column.id] += value
                            break
                elif column.type == "total":
                    totals.setdefault(column.id, 0)
                    grand_totals.setdefault(column.id, 0)
                    value = total
                    totals[column.id] += value
                    grand_totals[column.id] += value
                    total = 0
                    style = styles["total_number_style"]
                if value:
                    sheet.write(offset, c_index + 1, value, style)
            offset += 1
        
        for c_index, column in enumerate(columns):
            if column.id in totals:
                sheet.write(offset, c_index + 1, totals[column.id], styles["total_number_style"])
        offset += 2
        return offset

    def generate_xlsx_report(self, workbook, data, lines):
        payslips = self.env["hr.payslip"].browse(data["ids"])
        columns = self.env["hr.payslip.report.summary.xlsx.wizard.line"].browse(data["form"]["line_ids"])

        styles = {
            "base_style": workbook.add_format({"text_wrap": True}),
            "bold_style": workbook.add_format({"bold": True}),
            "title_style": workbook.add_format({"font_size": 20, "bold": True}),
            "section_style": workbook.add_format({"font_size": 16, "bold": True}),
            "header_bold_style": workbook.add_format({"text_wrap": True, "bold": True, "bg_color": "#e9ecef"}),
            "date_style": workbook.add_format({"text_wrap": True, "num_format": "yyyy-mm-dd"}),
            "datetime_style": workbook.add_format({"text_wrap": True, "num_format": "yyyy-mm-dd hh:mm:ss"}),
            "number_style": workbook.add_format({"num_format": "#,##0.00"}),
            "total_number_style": workbook.add_format({"num_format": "#,##0.00", "bold": True}),
            "divider_style": workbook.add_format({"font_size": 16, "bold": True, "bg_color": "#000000", "font_color": "#ffffff"}),
        }
        sheet = workbook.add_worksheet("Payslips")

        cut_off = payslips[0].date_from
        title = "Payroll: %s" % payslips[0].date_from
        for payslip in payslips:
            if payslip.date_from != cut_off:
                title = "Payroll: Mixed Cut-Off Period"
        sheet.write(0, 0, title, styles["title_style"])
        sheet.set_row(0, 25)
        offset = 2

        departments = set()
        if data["form"]["grouping"] == "department":
            for payslip in payslips:
                departments.add(payslip.employee_id.department_id)

        grand_totals = {}
        show_grand_totals = False
        if departments:
            for department in departments:
                offset = self._generate_lines(sheet, columns, payslips.filtered(lambda p: p.employee_id.department_id == department),
                    offset, styles, grand_totals, title=(department.name or "Undefined"))
            show_grand_totals = True
        else:
            offset = self._generate_lines(sheet, columns, payslips, offset, styles, grand_totals)
        
        if show_grand_totals:
            sheet.write(offset, 0, "Grand Totals", styles["divider_style"])
            sheet.write(offset + 1, 0, "Count", styles["header_bold_style"])
            sheet.write(offset + 2, 0, len(payslips), styles["bold_style"])
            sheet.set_row(offset, 21)
            for c_index, column in enumerate(columns):
                sheet.write(offset, c_index + 1, None, styles["divider_style"])
                if column.id in grand_totals:
                    header = self._get_column_header(column)
                    sheet.write(offset + 1, c_index + 1, header, styles["header_bold_style"])
                    sheet.write(offset + 2, c_index + 1, grand_totals[column.id], styles["total_number_style"])