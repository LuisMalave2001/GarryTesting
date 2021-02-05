# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveReportMatrixWizard(models.TransientModel):
    _name = "account.move.report.matrix.wizard.field"
    _description = "Journal Entry Matrix Report Wizard Field"
    _order = "sequence, id"

    sequence = fields.Integer(string="Sequence",
        required=True,
        default=100)
    field_id = fields.Many2one(string="Field",
        comodel_name="ir.model.fields",
        required=True)
    name = fields.Char("Header")
    wizard_id = fields.Many2one(string="Wizard",
        comodel_name="account.move.report.matrix.wizard",
        required=True,
        ondelete="cascade")