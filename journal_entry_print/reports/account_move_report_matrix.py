# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveReportMatrix(models.AbstractModel):
    _name = "report.journal_entry_print.account_move_report_matrix"
    _description = "Journal Entry Matrix Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        move_ids = self.env.context.get("active_ids", [])
        moves = self.env["account.move"].browse(move_ids)

        fields = self.env["account.move.report.matrix.wizard.field"].browse(data["form"]["field_ids"])
        journals = self.env["account.journal"]
        if data["form"]["group_by_journal"]:
            for move in moves:
                journals |= move.journal_id

        return {
            "doc_ids": move_ids,
            "doc_model": "account.move",
            "docs": moves,
            "data": data,
            "fields": fields,
            "journals": journals,
            "getattr": getattr,
            "self": self,
        }