# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountFollowupReport(models.AbstractModel):
    _inherit = "account.followup.report"

    def _get_columns_name(self, options):
        """
        Override
        Return the name of the columns of the follow-ups report
        """
        headers = super()._get_columns_name(options)
        headers.append(
            {'name': _('Student'), "class": "", 'style': 'text-align:right; white-space:nowrap;'})
        #            {'name': _('Date2'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
        #            {'name': _('Due Date2'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
        #            {'name': _('Source Document2'), 'style': 'text-align:center; white-space:nowrap;'},
        #            {'name': _('Communication2'), 'style': 'text-align:right; white-space:nowrap;'},
        #            {'name': _('Expected Date2'), 'class': 'date', 'style': 'white-space:nowrap;'},
        #            {'name': _('Excluded2'), 'class': 'date', 'style': 'white-space:nowrap;'},
        #            {'name': _('Total Due2'), 'class': 'number o_price_total', 'style': 'text-align:right; white-space:nowrap;'}
        #           ]
        # if self.env.context.get('print_mode'):
        #     headers = headers[:5] + headers[7:]  # Remove the 'Expected Date' and 'Excluded' columns
        return headers

    def _get_lines(self, options, line_id=None):
        lines = super()._get_lines(options, line_id)
        AccountMoveEnv = self.env["account.move"]

        student_ids = self.env["res.partner"]
        for line in lines:
            # line["unfoldable"] = line["unfolded"] = True
            if line.get("class", False):
                continue
            student_ids += line["account_move"].student_id
            student_name = line["account_move"].student_id.name
            line["columns"].append({"name": student_name})

        new_lines = list()
        student_ids = list(set(student_ids))
        for student_id in student_ids:
            student_invoice_ids = list(filter(
                lambda line: "account_move" in line and line["account_move"].student_id == student_id, lines))

            students_amount = 0
            student_lines = []
            for student_invoice_id in student_invoice_ids:
                student_invoice_id["parent_id"] = student_id
                students_amount += student_invoice_id["account_move"].amount_residual_signed

                student_lines.append(student_invoice_id)

            new_line = {
                "name": student_id.name,
                "level": 2,
                "unfoldable": True,
                "id": student_id.id,
                "columns": [
                    {"name": ""},
                    {"name": ""},
                    {"name": ""},
                    {"name": ""},
                    {"name": ""},
                    {"name": ""},
                    {"name": AccountMoveEnv._formatLang(students_amount)},
                ]
            }
            if self._context.get("print_mode"):
                new_line["columns"] = new_line["columns"][:4] + new_line["columns"][6:]
            new_lines.append(new_line)

            new_lines.extend(student_lines)

        no_students_lines = [line_id for line_id in lines if not line_id.get("account_move", self.env["account.move"]).student_id]

        no_students_amount = 0
        for no_student_line in no_students_lines:
            if "account_move" in no_student_line:
                no_students_amount += no_student_line["account_move"].amount_total_signed
            no_student_line["parent_id"] = 0

        new_line = {
            "name": _("Invoices without student"),
            "level": 2,
            "unfoldable": True,
            "id": 0,
            "columns": [
                {"name": ""},
                {"name": ""},
                {"name": ""},
                {"name": ""},
                {"name": ""},
                {"name": ""},
                {"name": AccountMoveEnv._formatLang(no_students_amount)},
            ]
        }
        if self._context.get("print_mode"):
            new_line["columns"] = new_line["columns"][:4] + new_line["columns"][6:]
        new_lines.append(new_line)
        new_lines.extend(no_students_lines)

        return new_lines
