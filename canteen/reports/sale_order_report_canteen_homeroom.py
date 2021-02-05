# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import OrderedSet

class SaleOrderReportCanteenHomeroom(models.AbstractModel):
    _name = "report.canteen.sale_order_report_canteen_homeroom"
    _description = "Canteen Report (Homeroom)"

    @api.model
    def _get_report_values(self, docids, data=None):
        orders = self.env["sale.order"].browse(data["order_ids"]).sorted(key=lambda o: (o.canteen_order_date, o.student_id.name))
        homerooms = OrderedSet(orders.mapped("student_id.homeroom"))
        dates = OrderedSet(orders.mapped("canteen_order_date"))
        return {
            "orders": orders,
            "homerooms": homerooms,
            "dates": dates,
            "self": self,
        }