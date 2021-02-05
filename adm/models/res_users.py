# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Users(models.Model):
    _inherit = "res.users"

    digital_signature = fields.Binary(string="Signature")
    application_ids = fields.One2many('adm.application', 'responsible_user_id')
