odoo.define('pos_analytics.pos_models', require => {

    const models = require('point_of_sale.models');

    const OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({

        initialize: function (attr,options) {
            OrderlineSuper.prototype.initialize.apply(this, arguments);
            if (options.json && options.json.analytic_account_id === undefined){
                this.analytic_account = this.product.analytic_account_id ? this.pos.db.analytic_account_by_id[this.product.analytic_account_id[0]] : {};
            } else if (!options.json){
                this.analytic_account = options.product && options.product.analytic_account_id ? this.pos.db.analytic_account_by_id[options.product.analytic_account_id[0]] : {};
            }
        },

        init_from_JSON: function(json) {
            OrderlineSuper.prototype.init_from_JSON.apply(this, arguments);
            this.analytic_account = this.pos.db.analytic_account_by_id[json.analytic_account_id];
        },

        export_as_JSON: function () {
            const orderLineJSON = OrderlineSuper.prototype.export_as_JSON.apply(this, arguments);

            if (this.analytic_account && this.analytic_account.id) {
                orderLineJSON.analytic_account_id = this.analytic_account.id;
            }

            return orderLineJSON
        },

        get_analytic_account: function () {
            return this.analytic_account;
        },
        set_analytic_account: function (analytic_account) {
            this.analytic_account = analytic_account;
            this.trigger('change', this);
        }
    });

});