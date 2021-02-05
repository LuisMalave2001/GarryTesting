# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    facts_accounting_system_id = fields.Integer("Accounting System")
    template_with_payment_id = fields.Many2one("ir.ui.view", string="Template with payment",
                                               domain=[("type", "=", "qweb")], default=lambda self: self.env.ref(
            'account.report_invoice_document_with_payments'))
    template_id = fields.Many2one("ir.ui.view", string="Template without payment",
                                  domain=[("type", "=", "qweb")],
                                  default=lambda self: self.env.ref('account.report_invoice_document'))

    facts_id_int = fields.Integer("Fact id")
    facts_id = fields.Char("Fact id (Char)", readonly=True, compute="_compute_facts_id")
    is_invoice = fields.Boolean()

    default_debit_account_code = fields.Char("default_debit_account_code", readonly=True, related="default_debit_account_id.code")
    default_credit_account_code = fields.Char("default_debit_account_code", readonly=True, related="default_credit_account_id.code")

    def _compute_facts_id(self):
        for record in self:
            record.facts_id = str(record.facts_id_int)
