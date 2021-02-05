odoo.define('pos_analytics.pos_screens', require => {

    const PosBaseWidget = require('point_of_sale.BaseWidget');
    const {ProductScreenWidget} = require('point_of_sale.screens');

    const SelectAnalyticWidget = PosBaseWidget.extend({
        template: 'SelectAnalyticWidget',

        events: {
            'click button.js_set_analytic': 'set_analytic_account'
        },

        set_analytic_account: function (event) {
            console.log('Setting analytic account');
            const order = this.pos.get_order();
            const selected_orderline = order.get_selected_orderline();
            const analytic_account_id = document.getElementById('analyticSelectionWidget-select').value;
            const analytic_account = this.pos.db.analytic_account_by_id[parseInt(analytic_account_id)]

            selected_orderline.set_analytic_account(analytic_account);
        }
    });

    ProductScreenWidget.include({
        start: function () {
            this._super.apply(this, arguments);

            this.selectAnalyticWidget = new SelectAnalyticWidget(this,{});
            this.selectAnalyticWidget.replace(this.$('.placeholder-SelectAnalyticWidget'));
        }

    });

    return {
        SelectAnalyticWidget
    }

});