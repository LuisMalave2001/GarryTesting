# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class TuitionPlanReport(models.Model):
    _name = "tuition.plan.report"
    _description = "Tuition Plan Report"
    _rec_name = 'date'
    _order = 'date desc'

    plan_id = fields.Many2one(string="Tuition Plan",
        comodel_name="tuition.plan",
        readonly=True)
    partner_id = fields.Many2one(string="Customer",
        comodel_name="res.partner",
        readonly=True)
    family_id = fields.Many2one(string="Family",
        comodel_name="res.partner",
        readonly=True)
    student_id = fields.Many2one(string="Student",
        comodel_name="res.partner",
        readonly=True)
    product_id = fields.Many2one(string="Product",
        comodel_name="product.product",
        readonly=True)
    price_subtotal = fields.Monetary(string="Subtotal",
        readonly=True)
    price_tax = fields.Monetary(string="Tax",
        readonly=True)
    price_total = fields.Monetary(string="Total",
        readonly=True)
    currency_id = fields.Many2one(string="Currency",
        comodel_name="res.currency",
        readonly=True)
    grade_level_id = fields.Many2one(string="Grade Level",
        comodel_name="school_base.grade_level",
        readonly=True)
    homeroom = fields.Char(string="Homeroom",
        readonly=True)
    date = fields.Date(string="Date",
        readonly=True)