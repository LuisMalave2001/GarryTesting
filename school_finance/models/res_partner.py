# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SchoolFinance(models.Model):
    _inherit = 'res.partner'

    family_invoice_ids = fields.Many2many("account.move", compute="_compute_family_invoice_ids", store=True, domain=[('type', '=', 'out_invoice')], context={
        'default_type': 'out_invoice',
        'type': 'out_invoice',
        'tree_view_ref': 'account.view_invoice_tree'
        })
    invoice_address_id = fields.Many2one("res.partner", string="Invoice Address")
    family_res_finance_ids = fields.One2many("school_finance.financial.res.percent", 'partner_id', string="Family resposability")
    student_invoice_ids = fields.One2many("account.move", "student_id", string="Student Invoices", domain=[('type', '=', 'out_invoice')])

    student_invoice_address_ids = fields.Many2many('res.partner', relation='res_partner_stu_inv_addr_rel',
                                      compute="compute_student_invoice_address_ids", store=True, required=False, column1='res_partner_id', column2='res_address_id',
                                      string='Student Invoice Addresses', readonly=True)

    invoice_amount_untaxed_signed = fields.Monetary(string="Total Tax Ecluded", compute="_compute_invoice_totals")
    invoice_amount_tax_signed = fields.Monetary(string="Total Tax", compute="_compute_invoice_totals")
    invoice_amount_total_signed = fields.Monetary(string="Total Total", compute="_compute_invoice_totals")
    invoice_amount_residual_signed = fields.Monetary(string="Total Amount Due", compute="_compute_invoice_totals")
    student_invoice_amount_untaxed_signed = fields.Monetary(string="Student Total Tax Ecluded", compute="_compute_invoice_totals")
    student_invoice_amount_tax_signed = fields.Monetary(string="Student Total Tax", compute="_compute_invoice_totals")
    student_invoice_amount_total_signed = fields.Monetary(string="Student Total Total", compute="_compute_invoice_totals")
    student_invoice_amount_residual_signed = fields.Monetary(string="Student Total Amount Due", compute="_compute_invoice_totals")
    family_invoice_amount_untaxed_signed = fields.Monetary(string="Family Total Tax Ecluded", compute="_compute_invoice_totals")
    family_invoice_amount_tax_signed = fields.Monetary(string="Family Total Tax", compute="_compute_invoice_totals")
    family_invoice_amount_total_signed = fields.Monetary(string="Family Total Total", compute="_compute_invoice_totals")
    family_invoice_amount_residual_signed = fields.Monetary(string="Family Total Amount Due", compute="_compute_invoice_totals")

    # Normal contact
    sc_invoice_ids = fields.Many2many('account.move', relation='res_partner_invoices_rel',
                                      compute="compute_sc_invoice_ids", store=True,
                                      string='Invoice lines', readonly=True, domain=[('type', '=', 'out_refund')])

    related_families_by_inv_address_ids = fields.One2many('res.partner', 'invoice_address_id')

    @api.onchange('family_ids')
    @api.depends('family_ids', 'family_ids.invoice_address_id')
    def compute_student_invoice_address_ids(self):
        for partner in self:
            partner.student_invoice_address_ids = partner.family_ids.mapped('invoice_address_id')

    @api.onchange('invoice_ids', 'sc_invoice_ids')
    @api.depends('invoice_ids')
    def compute_sc_invoice_ids(self):
        for partner in self:
            partner.sc_invoice_ids = partner.invoice_ids.filtered(lambda inv: inv.type in ('out_invoice', 'out_refund', 'out_receipt'))

    def _check_category_sum(self):
        for record in self:
            # categories = [{
            #                   category.category_id.id: category.percent
            #                   } for category in record.family_res_finance_ids]
            categories_ids = {category.category_id for category in record.family_res_finance_ids}

            for category_id in categories_ids:
                percent_sum = sum([category.percent for category in record.family_res_finance_ids if category.category_id == category_id])
                if percent_sum != 100:
                    raise UserError(_("Partner[%s]: %s Category: %s doesn't sum 100!") % (record.id, record.name, category_id.complete_name))

    @api.model
    def create(self, vals):
        """ We check family responsability """
        partners = super().create(vals)

        if "family_res_finance_ids" in vals:
            partners._check_category_sum()
        return partners

    def write(self, vals):
        """ We check family responsability """
        possitive = super().write(vals)

        if "family_res_finance_ids" in vals:
            self._check_category_sum()

        return possitive

    def _compute_family_invoice_ids(self):
        """
            Calculamos todos los invoices de la familia dependiento de sus miembros
        """
        for record in self:
            invoices = False
            if record.is_company:
                invoices = self.member_ids.invoice_ids + self.member_ids.student_invoice_ids + self.invoice_ids
            record.family_invoice_ids = invoices

    def _compute_invoice_totals(self):
        for partner in self:
            invoice_ids = partner.invoice_ids.filtered(lambda i: i.state != "cancel" and i.type in ["out_invoice", "out_refund", "out_receipt"])
            student_invoice_ids = partner.student_invoice_ids.filtered(lambda i: i.state != "cancel" and i.type in ["out_invoice", "out_refund", "out_receipt"])
            family_invoice_ids = partner.family_invoice_ids.filtered(lambda i: i.state != "cancel" and i.type in ["out_invoice", "out_refund", "out_receipt"])
            partner.invoice_amount_untaxed_signed = sum(invoice_ids.mapped("amount_untaxed_signed"))
            partner.invoice_amount_tax_signed = sum(invoice_ids.mapped("amount_tax_signed"))
            partner.invoice_amount_total_signed = sum(invoice_ids.mapped("amount_total_signed"))
            partner.invoice_amount_residual_signed = sum(invoice_ids.mapped("amount_residual_signed"))
            partner.student_invoice_amount_untaxed_signed = sum(student_invoice_ids.mapped("amount_untaxed_signed"))
            partner.student_invoice_amount_tax_signed = sum(student_invoice_ids.mapped("amount_tax_signed"))
            partner.student_invoice_amount_total_signed = sum(student_invoice_ids.mapped("amount_total_signed"))
            partner.student_invoice_amount_residual_signed = sum(student_invoice_ids.mapped("amount_residual_signed"))
            partner.family_invoice_amount_untaxed_signed = sum(family_invoice_ids.mapped("amount_untaxed_signed"))
            partner.family_invoice_amount_tax_signed = sum(family_invoice_ids.mapped("amount_tax_signed"))
            partner.family_invoice_amount_total_signed = sum(family_invoice_ids.mapped("amount_total_signed"))
            partner.family_invoice_amount_residual_signed = sum(family_invoice_ids.mapped("amount_residual_signed"))


class FinacialResponsabilityPercent(models.Model):
    _name = "school_finance.financial.res.percent"
    _description = "Realted model to finance responsabilty"

    partner_id = fields.Many2one("res.partner", string="Customer", domain=[("is_family", "=", False)])
    partner_family_ids = fields.Many2many(related="partner_id.family_ids")

    family_id = fields.Many2one("res.partner", required=True, string="Family")
    category_id = fields.Many2one("product.category", required=True, string="Category", domain=[("parent_id", "=", False)])
    percent = fields.Integer("Percent")

    @api.onchange('family_id')
    def _get_family_domain(self):
        self.ensure_one()
        family_ids = self.partner_id.family_ids.ids
        return {
            'domain': {
                'family_id': [("is_family", "=", True), ("is_company", "=", True), ('id', 'in', family_ids)]
                }
            }

    @api.model
    def create(self, vals):
        family_id = self.env["res.partner"].browse(vals["family_id"])
        if not family_id.is_family:
            raise ValidationError(_("%s is not a family!") % family_id.display_name)

        return super().create(vals)
