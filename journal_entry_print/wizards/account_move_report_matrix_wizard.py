# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

DEFAULT_FIELDS = [
    ("account.field_account_move__name", "Move"),
    ("account.field_account_move__ref", ""),
    ("account.field_account_move_line__name", ""),
    ("account.field_account_move_line__account_id", ""),
    ("account.field_account_move_line__partner_id", ""),
    ("account.field_account_move_line__debit", ""),
    ("account.field_account_move_line__credit", ""),
    ("account.field_account_move_line__date", ""),
    ("account.field_account_move_line__analytic_account_id", ""),
    ("account_reports.field_account_move_line__internal_note", ""),
    ("account.field_account_move_line__tax_ids", ""),
    ("account.field_account_move_line__tag_ids", "Tax Grids"),
]

class AccountMoveReportMatrixWizard(models.TransientModel):
    _name = "account.move.report.matrix.wizard"
    _description = "Journal Entry Matrix Report Wizard"

    def _default_field_ids(self):
        res = []
        for index, field in enumerate(DEFAULT_FIELDS):
            res.append((0, 0, {
                "name": field[1],
                "sequence": index,
                "field_id": self.env.ref(field[0]).id,
            }))
        return res

    group_by_journal = fields.Boolean(string="Group by Journal")
    field_ids = fields.One2many(string="Fields",
        comodel_name="account.move.report.matrix.wizard.field",
        inverse_name="wizard_id",
        default=_default_field_ids)

    def action_confirm(self):
        active_ids = self.env.context.get("active_ids", [])
        if not self.field_ids:
            raise ValidationError("Fields cannot be empty.")

        datas = {
            "ids": active_ids,
            "model": "account.move",
            "form": self.read()[0]
        }

        return self.env.ref("journal_entry_print.action_account_move_report_matrix").report_action([], data=datas)