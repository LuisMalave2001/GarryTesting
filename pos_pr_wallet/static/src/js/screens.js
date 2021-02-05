odoo.define("pos_pr_wallet.payment_register.screen", function (require) {

    const {InvoicePaymentRegisterScreenWidget} = require('pos_pr.payment_register.screens');
    const {PayWithWalletButton} = require('pos_pr_wallet.owl.components');

    InvoicePaymentRegisterScreenWidget.include({

        renderElement: function () {
            this._super.apply(this, arguments);
            this.invoicePaymentRegisterScreen.state.payWithWalletButton = PayWithWalletButton;
        }
    });

});
