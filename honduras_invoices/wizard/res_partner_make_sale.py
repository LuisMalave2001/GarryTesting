# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _

class ResPartnerMakeSale(models.TransientModel):
    _name = "res.partner.make.sale"
    _description = "Make a sale for a partner"

    order_line_ids = fields.Many2many("sale.order.line", string="Order Lines", ondelete="cascade")

    @api.model
    def create(self, values):
        if type(values) == dict and "order_line_ids" in values:
            partner_ids = self.env["res.partner"].browse(self.env.context.get("active_ids", []))
            for partner_id in partner_ids:
                SaleOrderEnv = self.env["sale.order"]

                SaleOrderEnv.create({
                    "date_order": datetime.now(), 
                    "partner_id": partner_id.id,
                    "order_line": values["order_line_ids"]
                })

            # We need to stop order_lines from being created
            # because it give us error, it needs a sale.order to be created
            del values["order_line_ids"]
        return super().create({}) #{'type': 'ir.actions.act_window_close'}
    


            