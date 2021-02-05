odoo.define('wallet.widgets', function(require) {
    "use strict";

    //var Widget = require("web.Widget");
    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');

    var Counter = AbstractField.extend({
        init: function(parent, name, record, options){
            this._super(parent, name, record, options);
            this.set("value", "");
        },

        start: function() {
            return this._super();
        },

        _renderReadonly: function() {
            let res_ids = [this.value.res_id] || this.value.res_ids;
            this.$el.html("<h1>" + this.value + "</h1>");
        }

    });

    registry.add('counter_widget', Counter);
});