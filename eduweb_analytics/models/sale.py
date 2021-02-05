# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def autofill_analytics(self):
        """ Autofill the analytics """

        # WHY SQL?
        # Well, this method of here can be used on many sale orders
        # The problem with this is that we need to do two for loops
        # and make a query in every loop, thanks that this algorithm is o^2
        # and that is a lot of query
        # But, using update from we can just use 1 query to do the same thing
        line_ids = self.mapped('order_line.id')

        if line_ids:
            placeholders = ', '.join(['%s'] * len(line_ids))
            query_line_update_analytics = """
            UPDATE sale_order_line
            SET    analytic_account_id = p_template.analytic_account_id
            FROM   product_product product
            INNER  JOIN product_template p_template
                   ON (product.product_tmpl_id = p_template.id)
            WHERE  sale_order_line.product_id = product.id
                   AND sale_order_line.id IN (%s)
            """ % placeholders

            self.env['sale.order.line'].invalidate_cache(fnames=['analytic_account_id'], ids=line_ids)
            self.env.cr.execute(query_line_update_analytics, line_ids)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_account_id = fields.Many2one('account.analytic.account')

    def _prepare_invoice_line(self):
        invoice_line_vals = super(SaleOrderLine, self)._prepare_invoice_line()

        if self.analytic_account_id:
            invoice_line_vals['analytic_account_id'] = self.analytic_account_id.id

        return invoice_line_vals
