# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.school_base.models.res_partner import SELECT_STATUS_TYPES

class TuitionPlan(models.Model):
    _name = "tuition.plan"
    _description = "Tuition Plan"

    name = fields.Char(string="Name",
        required=True)
    active = fields.Boolean(string="Active",
        default=True)
    period_type = fields.Selection(string="Period Type",
        selection=[
            ("fiscal_year","Fiscal Year"),
            ("year_after","Year After"),
            ("manual","Manual")],
        default="fiscal_year",
        required=True)
    reference_date = fields.Date(string="Reference Date",
        help="Used to identify the period based on the selected period type")
    period_date_from = fields.Date(string="Period Start",
        compute="_compute_period_dates",
        required=True,
        readonly=False,
        store=True,
        help="Autocomputed based on the selected reference date and period type")
    period_date_to = fields.Date(string="Period End",
        compute="_compute_period_dates",
        required=True,
        readonly=False,
        store=True,
        help="Autocomputed based on the selected reference date and period type")
    category_id = fields.Many2one(string="Category",
        comodel_name="product.category",
        required=True,
        domain="[('parent_id','=',False)]",
        help="Category of the products included in this tuition plan")
    automation = fields.Selection(string="Automation",
        selection=[
            ("quotation", "Create Quotation"),
            ("sales_order", "Create Sales Order"),
            ("sales_order_email", "Create Sales Order and send Sales Order by email"),
            ("draft_invoice", "Create Sales Order and Draft Invoice"),
            ("posted_invoice", "Create Sales Order and Posted Invoice"),
            ("posted_invoice_email", "Create Sales Order and Posted Invoice and send Invoice by email"),
            ("posted_invoice_stmt_email", "Create Sales Order and Posted Invoice and send Statement by email")],
        required=True,
        default="quotation",
        help="Specify what will automatically be created when an installment of this tuition plan is executed")
    first_charge_date = fields.Date(string="First Charge Date",
        required=True,
        help="The first date of the installments")
    payment_term_id = fields.Many2one(string="Payment Terms",
        comodel_name="account.payment.term",
        help="Payment term for the order and/or invoice generated.")
    first_due_date = fields.Date(string="First Due Date",
        help="Select the day of the due date. Only the day is used. Required if no payment term is set.")
    discount_ids = fields.One2many(string="Multi-child Discounts",
        comodel_name="tuition.plan.discount",
        inverse_name="plan_id",
        help="Discounts to apply based on the number of enrolled students in a family. Only enrolled students with the date of birth set is included.")
    installment_ids = fields.One2many(string="Installments",
        comodel_name="tuition.plan.installment",
        inverse_name="plan_id",
        help="Installment dates generated for the tuition plan based on the first charge date")
    override_installment_dates = fields.Boolean(string="Override Installment Dates")
    product_ids = fields.One2many(string="Products",
        comodel_name="tuition.plan.product",
        inverse_name="plan_id",
        help="Product to include in the order and/or invoice generated")
    company_id = fields.Many2one(string="Company",
        comodel_name="res.company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company)
    grade_level_ids = fields.Many2many(string="Grade Levels",
        comodel_name="school_base.grade_level",
        required=True,
        help="Grade levels to which this tuition plan applies and to whom it will generate order/invoice for")
    analytic_account_id = fields.Many2one(string="Analytic Account",
        comodel_name="account.analytic.account")
    default = fields.Boolean(string="Default",
        help="Specify if this tuition plan should be auto-assigned to students if they don't have any that overlaps with this plan")
    partner_ids = fields.Many2many(string="Students",
        comodel_name="res.partner",
        relation="partner_tuition_plan_rel",
        domain="[('grade_level_id','in',grade_level_ids)]",
        help="Students to which this tuition plan was manually assigned")
    discount_product_id = fields.Many2one(string="Discount Product",
        comodel_name="product.product",
        help="Product to use when adding multi-child discount lines")
    default_partner_ids = fields.Many2many(string="Default Students",
        comodel_name="res.partner",
        compute="_compute_default_partner_ids")
    use_student_payment_term = fields.Boolean(string="Use Student Payment Terms",
        help="If checked, the invoice payment terms is taken from the student if any")
    report_ids = fields.One2many(string="Report Lines",
        comodel_name="tuition.plan.report",
        inverse_name="plan_id")
    apply_for_status = fields.Selection(string="Apply for Status",
        selection=SELECT_STATUS_TYPES,
        help="Will only apply for students with matching status. If empty, applies to any status.",
        default="enrolled")

    @api.constrains("default", "grade_level_ids", "period_date_from", "period_date_to", "category_id", "active")
    def _check_default(self):
        for plan in self.filtered(lambda p: p.default):
            matched = self.search([
                "&", ("id","!=",plan.id),
                "&", ("default","=",True),
                "&", ("category_id","=",plan.category_id.id),
                "&", ("grade_level_ids","in",plan.grade_level_ids.ids),
                "|", ("period_date_from","=",plan.period_date_from),
                     ("period_date_to","=",plan.period_date_to)], limit=1)
            if matched:
                raise ValidationError(
                    "Unable to set as default. This tuition plan overlaps with %s (ID %d)." % (matched.name, matched.id))
    
    @api.constrains("partner_ids", "grade_level_ids", "period_date_from", "period_date_to", "category_id", "active")
    def _check_partner_ids(self):
        for plan in self:
            plan.partner_ids._check_tuition_plan_ids()

    @api.depends("reference_date", "period_type")
    def _compute_period_dates(self):
        for plan in self:
            date_from = False
            date_to = False
            if plan.reference_date:
                if plan.period_type == "fiscal_year":
                    dates = plan.company_id.compute_fiscalyear_dates(plan.reference_date)
                    date_from = dates["date_from"]
                    date_to = dates["date_to"]
                if plan.period_type == "year_after":
                    date_from = plan.reference_date
                    date_to = date_from + relativedelta(years=1, days=-1)
            plan.period_date_from = date_from
            plan.period_date_to = date_to

    @api.constrains("first_charge_date", "period_date_to")
    def _compute_installment_ids(self):
        for plan in self:
            plan.installment_ids.unlink()
            if not plan.first_charge_date:
                continue
            installment_ids = []
            months = 0
            installment_date = plan.first_charge_date + relativedelta(months=months)
            while installment_date <= plan.period_date_to:
                installment_ids.append((0, 0, {
                    "date": installment_date,
                }))
                months += 1
                installment_date = plan.first_charge_date + relativedelta(months=months)
            plan.installment_ids = installment_ids
    
    def get_overlapping_plans(self):
        self.ensure_one()
        return self.search([
            "&", ("category_id","=",self.category_id.id),
            "&", ("grade_level_ids","in",self.grade_level_ids.ids),
            "!", "|", ("period_date_to","<",self.period_date_from),
                      ("period_date_from",">",self.period_date_to)
        ])
    
    def _compute_default_partner_ids(self):
        for plan in self:
            result = []
            if plan.default:
                students = self.env["res.partner"].search([
                    ("person_type","=","student"),
                    ("tuition_plan_ids","=",False),
                    ("grade_level_id","in",plan.grade_level_ids.ids)
                ])
                result = students.ids
            plan.default_partner_ids = result
    
    def action_open_report(self):
        self.ensure_one()
        action = self.env.ref("tuition_plan.tuition_plan_report_action").read()[0]
        context = eval(action["context"])
        context.update({
            "search_default_plan_id": self.id,
        })
        action["context"] = context
        return action
    
    def action_generate_forecast(self):
        report_obj = self.env["tuition.plan.report"]
        plan_reports = report_obj.search([("plan_id","in",self.ids)])
        plan_reports.unlink()
        for plan in self:
            record_data = []
            for installment in plan.installment_ids:
                self._cr.execute("SAVEPOINT tuition_plan_report")
                sales = installment.with_context(
                    override_sale_order_name="For Tuition Plan Report",
                    automation="quotation").execute()
                for sale in sales:
                    for line in sale.order_line:
                        record_data.append({
                            "plan_id": plan.id,
                            "partner_id": sale.partner_id.id,
                            "family_id": sale.family_id.id,
                            "student_id": sale.student_id.id,
                            "product_id": line.product_id.id,
                            "price_subtotal": line.price_subtotal,
                            "price_tax": line.price_tax,
                            "price_total": line.price_total,
                            "grade_level_id": sale.student_id.grade_level_id.id,
                            "currency_id": sale.currency_id.id,
                            "homeroom": sale.student_id.homeroom,
                            "date": installment.date,
                        })
                try:
                    self._cr.execute("ROLLBACK TO SAVEPOINT tuition_plan_report")
                    self.pool.clear_caches()
                    self.pool.reset_changes()
                except psycopg2.InternalError:
                    pass
            for data in record_data:
                report_obj.create(data)