# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderReportCanteenStudent(models.AbstractModel):
    _name = "report.canteen.sale_order_report_canteen_student"
    _description = "Canteen Report (Student)"

    @api.model
    def _get_report_values(self, docids, data=None):
        orders = self.env["sale.order"].browse(data["order_ids"]).sorted(key=lambda o: (o.canteen_order_date, o.student_id.name))
        students = orders.mapped("student_id")
        dates = set(orders.mapped("canteen_order_date"))
        return {
            "orders": orders,
            "students": students,
            "dates": dates,
            "self": self,
        }