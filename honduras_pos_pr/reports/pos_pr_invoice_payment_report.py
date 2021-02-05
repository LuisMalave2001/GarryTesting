# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import MissingError

class PosPrInvoicePaymentReport(models.AbstractModel):
    _name = "report.honduras_pos_pr.pos_pr_invoice_payment_report"
    _description = "POS Invoice Payment Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_obj = self.env["pos_pr.invoice.payment"]
        pos_session_id = data["form"]["pos_session_id"][0]
        grouping = data["form"]["grouping"]
        payments = payment_obj.search([("pos_session_id","=",pos_session_id)])
        if not payments:
            raise MissingError("There are no invoice payments related to this session.")

        if grouping == "method":
            groups = payments.mapped("payment_method_id")
        else:
            groups = payments.mapped("payment_group_id")

        return {
            "doc_ids": payments.ids,
            "doc_model": "pos_pr.invoice.payment",
            "docs": payments,
            "groups": groups,
            "grouping": grouping,
            "session": self.env["pos.session"].browse(pos_session_id),
            "getattr": getattr,
        }