odoo.define("pos_pr_hr.gui", function (require) {

    const posHrChrome = require('pos_hr.chrome');

    posHrChrome.HeaderCloseButtonWidget.include({
        start: function () {
            if (this.pos.config.module_pos_hr) {
                this.pos.bind('change:cashier', this._restart_payment_view, this);
            }
            return this._super.apply(this, arguments);
        },

        _restart_payment_view: function () {
            if (this.pos.gui.get_current_screen() === 'pos_invoice_payment_register_widget') {
                this.pos.gui.current_screen.show();
            }
        }
    });

});
