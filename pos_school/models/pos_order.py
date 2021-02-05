# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import copy


class PosOrder(models.Model):
    _inherit = "pos.order"

    student_id = fields.Many2one('res.partner', domain='[("person_type", "=", "student")]')
    family_id = fields.Many2one('res.partner', domain='[("is_family", "=", True)]')
    skip_stock_picking = fields.Boolean()

    @api.model
    def create_from_ui(self, orders, draft=False):

        orders_to_create = []
        separated_orders_by_family = []
        for order in orders:
            order_data = order['data']
            if 'partner_id' in order_data:
                student_id = self.env['res.partner'].browse(order_data['partner_id'])
                if not student_id.person_type == 'student':
                    orders_to_create.append(order)
                else:
                    # We build several order_data and depending on family responsability
                    partner_responsible_categ = {category.category_id for category in student_id.family_res_finance_ids}
                    if 'lines' in order_data and order_data['lines']:
                        lines = order_data['lines']

                        for index, family_id in enumerate(student_id.family_ids):
                            order_lines = []
                            currency = self.env['pos.session'].browse(order_data['pos_session_id']).currency_id

                            # Retrieving data from lines
                            for line in lines:
                                if line[0] == 0:

                                    # We just clone it
                                    line_dict = dict(line[2])

                                    # Check if there is a responsable partner for this category
                                    product_id = self.env["product.product"].browse([line_dict["product_id"]])
                                    parent_category_id = product_id.categ_id

                                    while parent_category_id:
                                        if parent_category_id in partner_responsible_categ:
                                            break
                                        parent_category_id = parent_category_id.parent_id

                                    if not parent_category_id:
                                        raise UserError(_("%s doesn't have a responsible family for %s") % (student_id.name, product_id.categ_id.complete_name))

                                    percent_sum = sum([category.percent for category in student_id.family_res_finance_ids if
                                                       category.category_id == parent_category_id and category.family_id == family_id])
                                    percent_sum /= 100

                                    # Ps = Pu * Qnty
                                    # Ps_with_percent = Pu * PercentSum * Qnty
                                    # Ps * PercentSum = Pu * PercentSum * Qnty
                                    # Then Ps_with_percent = Ps * PercentSum
                                    # if index != 0:
                                    #     line_dict["qty"] = 0
                                    line_dict["price_unit"] = currency.round(line_dict["price_unit"] * percent_sum)
                                    line_dict["price_subtotal"] = currency.round(line_dict["price_subtotal"] * percent_sum)
                                    line_dict["price_subtotal_incl"] = currency.round(line_dict["price_subtotal_incl"] * percent_sum)

                                    if any([line_dict["price_unit"], line_dict["price_subtotal"], line_dict["price_subtotal_incl"]]):
                                        order_lines.append((0, 0, line_dict))

                            if order_lines:
                                family_order = copy.deepcopy(order)
                                # family_order['data'] = dict(order['data'])
                                family_order_data = family_order['data']
                                # if 'statement_ids' in order['data']:
                                #     family_order_data['statement_ids'] = order['data']['statement_ids'].copy()

                                if index != 0:
                                    family_order_data['skip_stock_picking'] = True

                                amount_total = order['data']['amount_total']
                                family_order_total = sum(map(lambda line: line[2]['price_subtotal_incl'], order_lines))

                                # This percent is from 0 to 1
                                amount_total_percent = family_order_total / amount_total
                                if 'statement_ids' in family_order_data and family_order_data['statement_ids']:
                                    if 'amount_return' in family_order_data:
                                        family_order_data["amount_return"] = currency.round(family_order_data["amount_return"] * amount_total_percent)
                                    for payment in family_order_data['statement_ids']:
                                        payment_vals = payment[2]
                                        payment_vals['amount'] = currency.round(payment_vals['amount'] * amount_total_percent)

                                if 'name' in family_order_data:
                                    family_order_data['name'] = "%s-%s" % (family_order_data['name'], family_id.id)

                                if 'id' in family_order:
                                    family_order['id'] = "%s-%s" % (family_order['id'], family_id.id)

                                family_order_data.update({
                                    'partner_id': family_id.invoice_address_id.id,
                                    'student_id': student_id.id,
                                    'family_id': family_id.id,
                                    'lines': order_lines,
                                    'amount_total': currency.round(amount_total_percent * amount_total),
                                    })

                                separated_orders_by_family.append(family_order)
        order_vals_list = orders_to_create + separated_orders_by_family
        order_response_vals = super(PosOrder, self).create_from_ui(order_vals_list, draft)

        if order_response_vals:

            order_names = list(map(lambda order_vals: order_vals['data']['name'], order_vals_list))
            order_vals_ids = set(map(lambda order_vals: order_vals['pos_reference'] in order_names and order_vals['id'], order_response_vals))
            if order_vals_ids:
                order_ids = self.browse(order_vals_ids)
                order_ids._onchange_amount_all()
                for order_id in order_ids:
                    order_id.action_pos_order_paid()
                    if order_id.to_invoice and order_id.state == 'paid':
                        order_id.action_pos_order_invoice()
        # Don't ask just 🐡
        return order_response_vals

    def _prepare_invoice_vals(self):
        invoice_vals = super(PosOrder, self)._prepare_invoice_vals()

        invoice_vals.update({
            'student_id': self.student_id.id,
            'family_id': self.family_id.id,
            })

        return invoice_vals

    def create_picking(self):
        if not self.skip_stock_picking:
            return super(PosOrder, self).create_picking()

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)

        order_fields.update({
            'skip_stock_picking': ui_order.get('skip_stock_picking', False),
            'student_id': ui_order.get('student_id', False),
            'family_id': ui_order.get('family_id', False),
            })

        return order_fields
