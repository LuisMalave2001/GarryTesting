# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class ResPartnerMakeSale(models.TransientModel):
    _name = "res.partner.make.sale"
    _description = "Make a sale for a partner"

    order_line_ids = fields.Many2many("sale.order.line", string="Order Lines", ondelete="cascade")
    journal_id = fields.Many2one("account.journal", string="Journal", domain=[("type", "=", "sale")])
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', check_company=True,  # Unrequired company
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="The analytic account related to a sales order.")

    # Invoice Date
    invoice_date_due = fields.Datetime(string='Due Date')
    invoice_date = fields.Datetime(string='Invoice Date')
    period_start = fields.Date(string="Period Start")
    period_end = fields.Date(string="Period End")

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', check_company=True,  # No-required company
                                   domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                   help="If you change the pricelist, only newly added lines will be affected.")

    separate_by_financial_responsability = fields.Boolean(default=True)
    sales_ids = fields.Many2many('sale.order')
    payment_term_id = fields.Many2one(string="Payment Terms", comodel_name="account.payment.term", help="Payment term for the generated order.")
    use_student_payment_term = fields.Boolean(string="Use Student Payment Terms", help="If checked, the sale order payment terms is taken from the student if any.")

    # partner_ids
    @api.model
    def create(self, values):
        if "sales_ids" not in values:
            values["sales_ids"] = list()

        if type(values) == dict and "order_line_ids" in values:
            partner_ids = self.env["res.partner"].browse(self.env.context.get("active_ids", []))

            SaleOrderEnv = self.env["sale.order"]
            sale_id = self.env["sale.order"]
            ProductEnv = self.env["product.product"]
            sales = self.env["sale.order"]

            line_ids = values["order_line_ids"]

            for partner_id in partner_ids:
                partner_pricelist = partner_id.property_product_pricelist and partner_id.property_product_pricelist.id or False
                pricelist_id = values.setdefault("pricelist_id", False)

                sale_pricelist = pricelist_id if pricelist_id else partner_pricelist
                partner_responsible_categ = {category.category_id for category in partner_id.family_res_finance_ids}

                if partner_id.person_type == 'student' and values["separate_by_financial_responsability"]:

                    # We build several sale order depending on
                    for family_id in partner_id.family_ids:
                        sale_dict = dict()

                        if not family_id.invoice_address_id:
                            raise UserError(_("The student (%s[%s])'s family %s[%s] doesn't have an invoice address!") % (partner_id.name, partner_id.id, family_id.name, family_id.id))

                        sale_dict["partner_id"] = family_id.invoice_address_id.id
                        sale_dict["student_id"] = partner_id.id
                        sale_dict["family_id"] = family_id.id

                        order_line = []

                        for line in line_ids:
                            if line[0] == 0:

                                # We just clone it
                                line_dict = dict(line[2])

                                product_id = ProductEnv.browse([line_dict["product_id"]])
                                parent_category_id = product_id.categ_id

                                while parent_category_id:
                                    if parent_category_id in partner_responsible_categ:
                                        break
                                    parent_category_id = parent_category_id.parent_id

                                if not parent_category_id:
                                    raise UserError(_("%s[%s] doesn't have a responsible family for %s") % (partner_id.name, partner_id.id, product_id.categ_id.complete_name))

                                percent_sum = sum([category.percent for category in partner_id.family_res_finance_ids if
                                                   category.category_id == parent_category_id and category.family_id == family_id])
                                percent_sum /= 100

                                line_dict["price_unit"] *= percent_sum

                                if line_dict["price_unit"] != 0:
                                    order_line.append((0, 0, line_dict))

                        if not order_line:
                            continue

                        sale_id = SaleOrderEnv.create({
                            "date_order": datetime.now(),
                            "partner_id": sale_dict["partner_id"],
                            "student_id": sale_dict["student_id"],
                            "family_id": sale_dict["family_id"],
                            "analytic_account_id": values["analytic_account_id"],
                            "journal_id": values["journal_id"],
                            "order_line": order_line,
                            "invoice_date": values["invoice_date"],
                            "invoice_date_due": values["invoice_date_due"],
                            "payment_term_id": values["payment_term_id"],
                            "period_start": values["period_start"],
                            "period_end": values["period_end"],
                            "pricelist_id": sale_pricelist,
                            })
                        sales = sales + sale_id
                else:
                    sale_id = SaleOrderEnv.create({
                        "date_order": datetime.now(),
                        "partner_id": partner_id.id,
                        "analytic_account_id": values["analytic_account_id"],
                        "journal_id": values["journal_id"],
                        "order_line": values["order_line_ids"],
                        "invoice_date": values["invoice_date"],
                        "invoice_date_due": values["invoice_date_due"],
                        "payment_term_id": values["payment_term_id"],
                        "period_start": values["period_start"],
                        "period_end": values["period_end"],
                        "pricelist_id": sale_pricelist,
                        })
                sales = sales + sale_id

            if sales:
                for sale in sales:
                    if values["use_student_payment_term"] and sale.student_id and sale.student_id.property_payment_term_id:
                        sale.payment_term_id = sale.student_id.property_payment_term_id.id
                        sale.invoice_date_due = False
                values["sales_ids"].append((6, 0, sales.ids))  # del values["order_line_ids"]

        # We need to stop order_lines from being created
        # because it give us error, they need a sale.order to be created
        del values["order_line_ids"]

        if not values["sales_ids"]:
            del values["sales_ids"]
        return super(ResPartnerMakeSale, self).create(values)  # {'type': 'ir.actions.act_window_close'}

    def go_to_invoices(self):
        context = self._context
        active_ids = self.sales_ids.ids
        return {
            'name': _("Sale Orders"),
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            "domain": [("id", "in", self.sales_ids.ids)],
            'target': 'current',
            }
