# -*- coding: utf-8 -*-

from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from ast import literal_eval


class SaleOrderForStudents(models.Model):
    """ This modify the default sale order behaviour """
    _inherit = "sale.order"

    journal_id = fields.Many2one("account.journal", string="Journal", domain="[('type', '=', 'sale')]")
    
    # Invoice Date
    invoice_date_due = fields.Datetime(string='Due Date', readonly=True, states={'draft': [('readonly', False)]})
    invoice_date = fields.Datetime(string='Invoice Date', readonly=True, states={'draft': [('readonly', False)]})
    period_start = fields.Date(string="Period Start", readonly=True, states={'draft': [('readonly', False)]})
    period_end = fields.Date(string="Period End", readonly=True, states={'draft': [('readonly', False)]})

    # School fields
    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family", domain=[('is_family', '=', True)])

    invoice_status_color = fields.Integer(string="Invoice Status Color", compute="compute_invoice_status_color")

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath('//field[@name="payment_term_id"]'):
    #             attrs = literal_eval(node.get('attrs', "{}"))
    #
    #             readonly_domain = attrs.get("readonly", [])
    #             readonly_domain.append(('state', '!=', 'draft'))
    #             attrs["readonly"] = readonly_domain
    #
    #             node.set("attrs", attrs)
    #
    #         res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res

    def compute_invoice_status_color(self):
        for order in self:
            result = 0
            if order.invoice_status == "no":
                result = 1 #red
            elif order.invoice_status == "to invoice":
                result = 3 #yellow
            elif order.invoice_status == "invoiced":
                result = 10 #green
            order.invoice_status_color = result

    def _student_receivable(self):
        self.ensure_one()
        receivable_behaviour = self.env["ir.config_parameter"].sudo().get_param('school_finance.receivable_behaviour')
        return receivable_behaviour == 'student' and self.student_id.person_type == 'student'

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()

        if self.journal_id:
            invoice_vals["journal_id"] = self.journal_id.id

        if self.invoice_date:
            invoice_vals["invoice_date"] = self.invoice_date
            invoice_vals["date"] = self.invoice_date

        if self._student_receivable():
            invoice_vals["receivable_account_id"] = self.student_id.property_account_receivable_id.id

        if self.family_id:
            invoice_vals["family_id"] = self.family_id.id

        if not self.payment_term_id:
            invoice_vals["invoice_date_due"] = self.invoice_date_due

        if self.student_id:
            invoice_vals["student_id"] = self.student_id.id
            invoice_vals["student_grade_level"] = self.student_id.grade_level_id.id
            invoice_vals["student_homeroom"] = self.student_id.homeroom
        
        if self.period_start:
            invoice_vals["period_start"] = self.period_start

        if self.period_end:
            invoice_vals["period_end"] = self.period_end

        return invoice_vals

    def _create_invoices(self, grouped=False, final=False):
        all_moves = super()._create_invoices(grouped, final)

        for order in self:
            # Basically, we change the move_ids receivable account to student if the settings allow it
            order_created_invoice_ids = all_moves & order.invoice_ids

            order._set_receivable_to_invoices(order_created_invoice_ids)

        return all_moves

    def _set_receivable_to_invoices(self, invoice_ids):
        self.ensure_one()
        if self._student_receivable():
            invoice_ids.set_receivable_account()


class SaleOrderLine(models.Model):
    """ Sale Order Line """
    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        super().product_uom_change()
        if not self.order_id.pricelist_id and not self.order_id.partner_id:
            self.price_unit = self.product_id.lst_price

    @api.onchange('product_id')
    def product_id_change(self):
        res = super().product_id_change()

        if not self.order_id.pricelist_id and not self.order_id.partner_id:
            price_unit = self.product_id.lst_price
            self.write({"price_unit": price_unit})
        
        return res
        