# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, SUPERUSER_ID

class TuitionPlanInstallment(models.Model):
    _name = "tuition.plan.installment"
    _description = "Tuition Plan Installment"
    _order = "date"
    _rec_name = "date"

    date = fields.Date(string="Date",
        help="Date to trigger installment")
    plan_id = fields.Many2one(string="Tuition Plan",
        comodel_name="tuition.plan",
        required=True,
        ondelete="cascade")
    product_ids = fields.Many2many(string="Products",
        comodel_name="tuition.plan.product",
        relation="plan_product_plan_installment_rel",
        help="Products to include in order and/or invoice")
    
    def _get_end_date(self):
        self.ensure_one()
        installments = self.plan_id.installment_ids.filtered(lambda i: i.product_ids)
        installment_ids = installments.ids
        if self.id == installment_ids[-1]:
            return self.plan_id.period_date_to
        next_installment = installments[installment_ids.index(self.id) + 1]
        return next_installment.date - relativedelta(days=1)
    
    def execute(self):
        make_sale_obj = self.env["res.partner.make.sale"]
        make_sale = make_sale_obj
        for installment in self.filtered(lambda i: i.plan_id.active and i.product_ids):
            plan = installment.plan_id
            students = self._context.get("students") or (plan.partner_ids | plan.default_partner_ids)
            students = students.filtered(lambda s: s.grade_level_id in plan.grade_level_ids)
            if plan.apply_for_status:
                students = students.filtered(lambda s: s.student_status_id == plan.apply_for_status)
            if not students:
                continue
            invoice_due_date = False
            if not plan.payment_term_id and plan.first_due_date:
                invoice_date_due_day = plan.first_due_date.day
                months = 0 if invoice_date_due_day >= installment.date.day else 1
                invoice_due_date = installment.date + relativedelta(months=months, day=invoice_date_due_day)
            order_line_ids = [(6, 0, [])]
            for product in installment.product_ids:
                order_line_ids.append((0, 0, product._prepare_order_line_vals()))
            vals = {
                "invoice_date": installment.date,
                "invoice_date_due": invoice_due_date,
                "separate_by_financial_responsability": True,
                "analytic_account_id": plan.analytic_account_id.id,
                "journal_id": False,
                "order_line_ids": order_line_ids,
                "payment_term_id": plan.payment_term_id.id,
                "period_start": installment.date,
                "period_end": installment._get_end_date(),
                "use_student_payment_term": plan.use_student_payment_term,
            }
            make_sale = make_sale_obj.with_context(allowed_company_ids=[plan.company_id.id], active_ids=students.ids).create(vals)
            for sale in make_sale.sales_ids:
                if plan.discount_ids:
                    children = sale.family_id.member_ids\
                        .filtered(lambda m: m.person_type == "student" and m.student_status == "Enrolled")\
                        .sorted(lambda m: m.name)\
                        .sorted(lambda m: (m.grade_level_id.sequence or 0, m.grade_level_id.id or 0,
                            m.date_of_birth or fields.Date.context_today(self)), reverse=True).ids
                    if sale.student_id.id in children:
                        index = children.index(sale.student_id.id)
                    categories = set()
                    for discount in plan.discount_ids:
                        categories.add(discount.category_id)
                    for category in categories:
                        discounts = plan.discount_ids.filtered(lambda d: d.category_id == category)
                        category_index = len(discounts) - 1 if index >= len(discounts) else index
                        if category == False:
                            amount = sale.amount_total
                        else:
                            amount = sum(sale.order_line.filtered(lambda l: l.product_id.categ_id == category).mapped("price_total"))
                        if amount > 0:
                            sale.write({
                                "order_line": [(0, 0, {
                                    "product_id": plan.discount_product_id.id,
                                    "price_unit": min(-amount * discounts[index].percentage / 100, sale.amount_total),
                                })]
                            })
            automation = self._context.get("automation") or plan.automation
            if automation in ["sales_order", "sales_order_email", "draft_invoice", "posted_invoice", "posted_invoice_email", "posted_invoice_stmt_email"]:
                for sale in make_sale.sales_ids:
                    sale.action_confirm()
                    if automation in ["sales_order_email"]:
                        sale._send_order_confirmation_mail()
                    if automation in ["draft_invoice", "posted_invoice", "posted_invoice_email", "posted_invoice_stmt_email"]:
                        invoices = sale._create_invoices(grouped=True)
                        invoice_lines = invoices.invoice_line_ids
                        for product in installment.product_ids:
                            for line in invoice_lines:
                                if line.price_unit >= 0 and product.product_id == line.product_id and product.analytic_account_id:
                                    line.analytic_account_id = product.analytic_account_id.id
                        if automation in ["posted_invoice", "posted_invoice_email", "posted_invoice_stmt_email"]:
                            invoices.action_post()
                            if automation in ["posted_invoice_email"]:
                                template = self.env.ref("account.email_template_edi_invoice", raise_if_not_found=False)
                                if template:
                                    for invoice in invoices.with_user(SUPERUSER_ID):
                                        invoice.message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_paynow")
                            elif automation in ["posted_invoice_stmt_email"]:
                                for invoice in invoices:
                                    invoice.partner_id.email_statement = True

        return make_sale.sales_ids