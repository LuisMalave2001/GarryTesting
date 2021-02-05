# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrderReportCanteenWizard(models.TransientModel):
    _name = "sale.order.report.canteen.wizard"
    _description = "Canteen Report Wizard"

    report_type = fields.Selection(string="Type",
        selection=[
            ("student","By Student"),
            ("gradelevel","By Grade Level"),
            ("homeroom","By Homeroom")],
        required=True,
        default="student")
    student_ids = fields.Many2many(string="Students",
        comodel_name="res.partner",
        domain="[('person_type','=','student')]")
    from_date = fields.Date(string="From",
        required=True,
        default=fields.Date.today())
    to_date = fields.Date(string="To",
        required=True,
        default=fields.Date.today())
    include_unconfirmed = fields.Boolean(string="Include Unconfirmed",
        help="If checked, includes orders in quotation status")

    def action_confirm(self):
        self.ensure_one()
        domain = [
            ("is_canteen_order","=",True),
            ("canteen_order_date",">=",self.from_date),
            ("canteen_order_date","<=",self.to_date)
        ]

        if self.include_unconfirmed:
            domain.append(("state","in",["draft","sent","sale","done"]))
        else:
            domain.append(("state","in",["sale","done"]))

        if self.report_type == "student" and self.student_ids:
            domain.append(("student_id","in",self.student_ids.ids))
        
        orders = self.env["sale.order"].search(domain)
        if not orders:
            raise ValidationError("No orders to print for given criteria.")

        datas = {
            "order_ids": orders.ids,
        }

        return self.env.ref("canteen.action_sale_order_report_canteen_" + self.report_type).report_action([], data=datas)