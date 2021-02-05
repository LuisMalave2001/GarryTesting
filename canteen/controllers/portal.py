# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime, time
from dateutil import parser
from pytz import timezone, UTC

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR
from odoo.tools import plaintext2html

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        families = request.env.user.partner_id.family_ids
        responsibilities = request.env.user.partner_id.family_ids.member_ids.family_res_finance_ids.filtered(lambda r: r.family_id in families)
        categories = responsibilities.category_id
        canteen_products = request.env["product.product"].sudo().search([("canteen_ok","=",True),("categ_id","child_of",categories.ids)])
        values["canteen_order_count"] = request.env["sale.order"].search_count([("is_canteen_order","=",True)])
        values["canteen_order_eligible"] = True if canteen_products else False
        values["user"] = request.env.user
        return values

    def _canteen_order_get_page_view_values(self, canteen_order, access_token, **kwargs):
        values = {
            "canteen_order": canteen_order,
            "user": request.env.user,
            "students": request.env["res.partner"].sudo().search([
                ("person_type","=","student"),
                ("id","in",request.env.user.partner_id.family_ids.mapped('member_ids').ids)]),
            "products": canteen_order and canteen_order.order_line.mapped("product_id").sudo() or request.env["product.product"].sudo(),
            "plaintext2html": plaintext2html,
        }
        res = self._get_page_view_values(canteen_order, access_token, values, "my_canteen_orders_history", True, **kwargs)
        if res.get("prev_record"):
            res["prev_record"] = res["prev_record"] and res["prev_record"].replace("/orders/","/canteen_order/")
        if res.get("next_record"):
            res["next_record"] = res["next_record"] and res["next_record"].replace("/orders/","/canteen_order/")
        return res

    @http.route(["/my/canteen_order/", "/my/canteen_order/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_canteen_orders(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in="name", **kw):
        values = self._prepare_portal_layout_values()
        canteen_order_obj = request.env["sale.order"]
        domain = []

        archive_groups = self._get_archive_groups("sale.order", domain)
        if date_begin and date_end:
            domain += [("canteen_order_date",">",date_begin),("canteen_order_date","<=",date_end)]
    
        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "canteen_order_date desc"},
            "name": {"label": _("Name"), "order": "name"},
        }
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        default_domain = [("is_canteen_order","=",True)]
        searchbar_filters = {
            "all": {"label": _("All"), "domain": default_domain},
            "draft": {"label": _("Draft"), "domain": [("state","in",["draft","sent"])] + default_domain},
            "confirmed": {"label": _("Confirmed"), "domain": [("state","in",["sale","done"])] + default_domain},
            "cancel": {"label": _("Cancelled"), "domain": [("state","=","cancel")] + default_domain},
        }
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]['domain']

        searchbar_inputs = {
            "name": {"input": "name", "label": _("Search in Order #")},
            "canteen_order_date": {"input": "canteen_order_date", "label": _("Search in Date"), "type": "date"},
            "student_id": {"input": "student_id", "label": _("Search in Student")},
        }
        if search and search_in:
            search_domain = []
            if search_in == "name":
                search_domain = OR([search_domain, [("name","ilike",search)]])
            elif search_in == "canteen_order_date":
                canteen_order_date = parser.parse(search)
                search_domain = OR([search_domain, [("canteen_order_date","=",canteen_order_date)]])
            elif search_in == "student_id":
                member_ids = request.env.user.partner_id.family_ids.mapped('member_ids').ids
                student_ids = request.env["res.partner"].sudo().search([("id","in",member_ids),("name","ilike",search)]).ids
                search_domain = OR([search_domain, [("student_id","in",student_ids)]])
            domain += search_domain

        canteen_order_count = canteen_order_obj.search_count(domain)
        pager = portal_pager(
            url="/my/canteen_order",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=canteen_order_count,
            page=page,
            step=self._items_per_page
        )

        canteen_orders = canteen_order_obj.search(domain, order=order, limit=self._items_per_page, offset=pager["offset"])
        request.session["my_canteen_orders_history"] = canteen_orders.ids[:100]

        values.update({
            "date": date_begin,
            "date_end": date_end,
            "canteen_orders": canteen_orders,
            "page_name": "canteen_order",
            "archive_groups": archive_groups,
            "default_url": "/my/canteen_order",
            "pager": pager,
            "searchbar_sortings": searchbar_sortings,
            "sortby": sortby,
            "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
            "filterby": filterby,
            "searchbar_inputs": searchbar_inputs,
            "search_in": search_in,
            "search": search,
        })
        return request.render("canteen.portal_my_canteen_orders", values)
    
    @http.route(["/my/canteen_order/<int:canteen_order_id>"], type="http", auth="user", website="True")
    def portal_my_canteen_order(self, canteen_order_id=None, access_token=None, **kw):
        canteen_order = request.env["sale.order"].browse(canteen_order_id)
        values = self._canteen_order_get_page_view_values(canteen_order, access_token, **kw)
        values["readonly"] = True
        return request.render("canteen.portal_my_canteen_order", values)
    
    @http.route(["/my/canteen_order/<int:canteen_order_id>/edit"], type="http", auth="user", website="True")
    def portal_my_canteen_order_edit(self, canteen_order_id=None, access_token=None, **kw):
        canteen_order = request.env["sale.order"].browse(canteen_order_id)
        values = self._canteen_order_get_page_view_values(canteen_order, access_token, **kw)
        return request.render("canteen.portal_my_canteen_order", values)
    
    @http.route(["/my/canteen_order/create"], type="http", auth="user", website="True")
    def portal_my_canteen_order_create(self, access_token=None, **kw):
        canteen_order = request.env["sale.order"]
        values = self._canteen_order_get_page_view_values(canteen_order, access_token, **kw)
        values["create_canteen_order"] = True
        return request.render("canteen.portal_my_canteen_order", values)

    @http.route(["/my/canteen_order/<int:canteen_order_id>/confirm"], type="http", auth="user", website="True")
    def portal_my_canteen_order_confirm(self, canteen_order_id=None, access_token=None, **kw):
        canteen_order = request.env["sale.order"].browse(canteen_order_id)
        url = canteen_order.get_portal_url()
        return request.redirect(url)
    
    @http.route(["/my/canteen_order/<int:canteen_order_id>/cancel"], type="http", auth="user", website="True")
    def portal_my_canteen_order_cancel(self, canteen_order_id=None, access_token=None, **kw):
        canteen_order = request.env["sale.order"].browse(canteen_order_id)
        canteen_order.sudo().action_cancel()
        return request.redirect("/my/canteen_order/" + str(canteen_order.id))

    @http.route(["/my/canteen_order/save"], type="http", auth="user", methods=["POST"], website="True")
    def portal_my_canteen_order_save(self, access_token=None, **kw):
        order_line = []
        line_ids = []
        for key, value  in kw.items():
            if "product_id_" in key:
                number = key.replace("product_id_", "")
                product_id = int(kw.get(key))
                product_uom_qty = float(kw.get("product_uom_qty_" + number))
                price_unit = float(kw.get("price_unit_" + number))
                line_id = int(kw.get("line_id_" + number))
                if line_id:
                    line_ids.append(line_id)
                    line_vals = (1, line_id, {
                        "product_id": product_id,
                        "product_uom_qty": product_uom_qty,
                        "price_unit": price_unit,
                    })
                else:
                    line_vals = (0, 0, {
                        "product_id": product_id,
                        "product_uom_qty": product_uom_qty,
                        "price_unit": price_unit,
                    })
                order_line.append(line_vals)

        student_id = int(kw.get("student_id"))
        family_id = request.env.user.family_ids.filtered(lambda f: student_id in f.member_ids.ids)[0].id
        vals = {
            "student_id": student_id,
            "family_id": family_id,
            "canteen_order_date": kw.get("canteen_order_date"),
            "commitment_date": kw.get("canteen_order_date"),
            "is_canteen_order": True,
            "order_line": order_line
        }

        if kw.get("id"): # edit
            res = request.env["sale.order"].browse(int(kw.get("id"))).sudo()
            deleted_line_ids = set(res.order_line.ids) - set(line_ids)
            for line_id in deleted_line_ids:
                vals["order_line"].append((2, line_id))
            res.write(vals)
        else: # create
            vals["partner_id"] = request.env.user.partner_id.id
            vals["state"] = "sent"
            res_obj = request.env["sale.order"].sudo()
            res = res_obj.create(vals)
        return request.redirect("/my/canteen_order/" + str(res.id))

    @http.route(["/canteen/get_product_details"], type="json", auth="user")
    def portal_my_canteen_order_get_product_details(self, product_id):
        vals = {
            "name": "-",
            "price_unit": "-",
        }
        if product_id:
            product = request.env["product.product"].sudo().browse(int(product_id))
            vals["name"] = product.description_sale or "-"
            vals["price_unit"] = product.lst_price
        vals["name"] = plaintext2html(vals["name"])
        return vals

    @http.route(["/canteen/get_available_products"], type="json", auth="user")
    def portal_my_canteen_order_get_available_products(self, student_id, date):
        if not date or not student_id:
            return {}
        
        families = request.env.user.partner_id.family_ids
        student = request.env["res.partner"].sudo().browse(int(student_id))
        responsibilities = student.family_res_finance_ids.filtered(lambda r: r.family_id in families)
        categories = responsibilities.category_id

        date = parser.parse(date)
        weekday = date.strftime("%A").lower()
        domain = [("canteen_ok","=",True),("categ_id","child_of",categories.ids)]
        availability = request.env["canteen.availability"].sudo().search([("date","=",date)])
        if availability:
            domain += ["|",("canteen_recur_" + weekday,"=",True),("canteen_availability_dates","in",availability.ids)]
        else:
            domain += [("canteen_recur_" + weekday,"=",True)]
        vals = request.env["product.product"].sudo().search(domain).read(["id", "name"])
        return vals