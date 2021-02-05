# -*- coding: utf-8 -*-

from odoo import models, fields


class Attachments(models.Model):
    _inherit = "ir.attachment"

    inquiry_id = fields.Many2one("adm.inquiry")
    application_passport_id = fields.Many2one('adm.application')
    application_residency_id = fields.Many2one('adm.application')
