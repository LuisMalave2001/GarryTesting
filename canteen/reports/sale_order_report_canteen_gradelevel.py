# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import OrderedSet

class SaleOrderReportCanteenGradeLevel(models.AbstractModel):
    _name = "report.canteen.sale_order_report_canteen_gradelevel"
    _description = "Canteen Report (Grade Level)"

    @api.model
    def _get_report_values(self, docids, data=None):
        orders = self.env["sale.order"].browse(data["order_ids"]).sorted(key=lambda o: (o.canteen_order_date, o.student_id.name))
        grade_levels = OrderedSet()
        for order in orders:
            grade_levels.add(order.student_id.grade_level_id)
        dates = OrderedSet(orders.mapped("canteen_order_date"))
        return {
            "orders": orders,
            "grade_levels": grade_levels,
            "dates": dates,
            "self": self,
        }