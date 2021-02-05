odoo.define("canteen.canteen_order_portal_form", function(require){
"use strict";

var publicWidget = require("web.public.widget");
var session = require('web.session');

publicWidget.registry.timeOffPortalForm = publicWidget.Widget.extend({
    selector: ".o_canteen_order_portal_form",
    events: {
        "click .o_canteen_order_portal_form_add_line": "_addLine",
        "click .o_canteen_order_portal_form_remove_line": "_removeLine",
        "change .o_canteen_order_portal_form_product_id": "_onchangeProduct",
        "change .o_canteen_order_portal_form_product_uom_qty": "_onchangeQuantity",
        "change .o_canteen_order_portal_form_canteen_order_date": "_updateProducts",
        "change .o_canteen_order_portal_form_student_id": "_updateProducts",
    },

    start: function () {
        var def = this._super.apply(this, arguments);
        return def
    },

    _addLine: function(ev) {
        var orig = ev.target.previousElementSibling.lastElementChild
        var orig_number = parseInt(orig.id.replace("line_",""))
        var new_number = orig_number + 1

        var line = orig.cloneNode(true);
        line.id = line.name = "line_" + new_number
        var line_id = line.querySelector("#line_id_" + orig_number)
        line_id.id = line_id.name = "line_id_" + new_number
        line_id.value = 0
        var product_id = line.querySelector("#product_id_" + orig_number)
        product_id.id = product_id.name = "product_id_" + new_number
        product_id.value = ""
        var name = line.querySelector("#name_" + orig_number)
        name.id = name.name = "name_" + new_number
        name.innerHTML = "<p>-</p>"
        var product_uom_qty = line.querySelector("#product_uom_qty_" + orig_number)
        product_uom_qty.id = product_uom_qty.name = "product_uom_qty_" + new_number
        product_uom_qty.value = ""
        var price_unit_text = line.querySelector("#price_unit_text_" + orig_number)
        price_unit_text.id = price_unit_text.name = "price_unit_text_" + new_number
        price_unit_text.innerHTML = "-"
        var price_unit = line.querySelector("#price_unit_" + orig_number)
        price_unit.id = price_unit.name = "price_unit_" + new_number
        price_unit.value = "-"
        var price_subtotal = line.querySelector("#price_subtotal_" + orig_number)
        price_subtotal.id = price_subtotal.name = "price_subtotal_" + new_number
        price_subtotal.innerHTML = "-"
        ev.target.previousElementSibling.append(line)
    },

    _removeLine: function(ev) {
        if (ev.target.parentElement.parentElement.parentElement.childElementCount > 1) {
            ev.target.parentElement.parentElement.remove()
        }
    },

    _onchangeProduct: function(ev) {
        var self = this
        self.active_product_id = ev.target.name.replace("product_id_", "")
        session.rpc("/canteen/get_product_details", {
            product_id: ev.target.value
        }).then(function (details) {
            self.$el.find("#name_" + self.active_product_id)[0].innerHTML = details["name"]
            self.$el.find("#price_unit_text_" + self.active_product_id)[0].innerHTML = details["price_unit"]
            self.$el.find("#price_unit_" + self.active_product_id)[0].value = details["price_unit"]
            self._updateSubtotal(self.active_product_id)
        })
    },

    _onchangeQuantity: function(ev) {
        this._updateSubtotal(ev.target.name.replace("product_uom_qty_", ""))
    },

    _updateSubtotal: function(product_id) {
        var quantity = parseFloat(this.$el.find("#product_uom_qty_" + product_id)[0].value)
        var price_subtotal = parseFloat(this.$el.find("#price_unit_text_" + product_id)[0].innerHTML) * quantity
        if (Number.isNaN(price_subtotal)) {
            price_subtotal = "-"
        }
        this.$el.find("#price_subtotal_" + product_id)[0].innerHTML = price_subtotal
    },

    _updateProducts: function(ev) {
        var self = this
        var student_id = this.$el.find("#student_id")[0].value
        var date = this.$el.find("#canteen_order_date")[0].value
        session.rpc("/canteen/get_available_products", {
            student_id: student_id,
            date: date,
        }).then(function (products) {
            var product_ids = self.$el.find(".o_canteen_order_portal_form_product_id")
            var names = self.$el.find(".o_canteen_order_portal_form_name")
            var product_uom_qtys = self.$el.find(".o_canteen_order_portal_form_product_uom_qty")
            var price_unit_texts = self.$el.find(".o_canteen_order_portal_form_price_unit_text")
            var price_units = self.$el.find(".o_canteen_order_portal_form_price_unit")
            var price_subtotals = self.$el.find(".o_canteen_order_portal_form_price_subtotal")

            var options = "<option value>--- Item ---</option>"
            _.forEach(products, function(product) {
                options += '<option value="' + product["id"] + '">' + product["name"] + '</option>'
            })
            _.forEach(product_ids, function(product_id) {
                product_id.value = ""
                product_id.innerHTML = options
            })
            _.forEach(names, function(name) {
                name.innerHTML = "<p>-</p>"
            })
            _.forEach(product_uom_qtys, function(product_uom_qty) {
                product_uom_qty.value = ""
            })
            _.forEach(price_unit_texts, function(price_unit_text) {
                price_unit_text.innerHTML = "-"
            })
            _.forEach(price_units, function(price_unit) {
                price_unit.value = "-"
            })
            _.forEach(price_subtotals, function(price_subtotal) {
                price_subtotal.innerHTML = "-"
            })
        })
    },
})
});