# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosPrInvoicePaymentReportWizard(models.TransientModel):
    _name = "pos_pr.invoice.payment.report.wizard"
    _description = "POS Invoice Payment Report Wizard"

    grouping = fields.Selection(string="Group By",
        selection=[
            ('method', 'Payment Method'), 
            ('group', 'Payment Group')],
        default='method',
        required=True)
    pos_session_id = fields.Many2one(string="POS Session",
        comodel_name="pos.session",
        required=True,
        default=lambda self: self.env["pos.session"].search([], limit=1).id)

    def action_confirm(self):
        active_ids = self.env.context.get("active_ids", [])
        datas = {
            "ids": active_ids,
            "model": "pos_pr.invoice.payment",
            "form": self.read()[0]
        }

        return self.env.ref("honduras_pos_pr.action_pos_pr_invoice_payment_report").report_action([], data=datas)