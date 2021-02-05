odoo.define('pos_wallet.components.LoadWalletPopup', function (require) {

    const PosBaseWidget = require('point_of_sale.BaseWidget');

    return PosBaseWidget.extend({
        init: function (parent, option) {
            this._super.apply(this, arguments);
        },
    });

});