odoo.define("pos_pr_wallet.owl.components", function (require) {
    /*
    * This is used to create all OWL components
    * */
    const store = require('pos_wallet.owl.store');

    const {PosWalletPaymentSTComponent, WalletPaymentCardCompoment} = require('pos_wallet.owl.components');
    const {Component, useState} = owl;
    const {InvoicePaymentReceiptScreenWidget} = require('pos_pr.screens.invoice_payment_receipt');

    const {_t} = require("web.core");

    class LoadWalletWithChangePopupRow extends Component {
        static props = ['walletRow'];
    }

    class LoadWalletWithChangePopupApp extends Component {

        constructor(parent, props) {
            super(parent, props);
            this.pos = props.pos;
        }

        walletsRows = useState([]);
        walletsRowsId = 1;

        add_new_wallet_row() {
            this.walletsRows.push({name: 'AAAAAH', id: this.walletsRowsId++});
        }

    }

    class PayInvoiceWithWalletPopupApp extends Component {
        static props = ['pos'];
        static components = {PosWalletPaymentSTComponent, WalletPaymentCardCompoment};

        paymentRegister = {
            format_currency(amount, precision) {
                return amount;
            }
        }

        paymentState = useState({
            invoice: {},
            walletAmounts: {},
        })

        get walletPaymentTotal() {
            return _.reduce(this.paymentState.walletAmounts, (memo, nextAmount) => memo + nextAmount, 0);
        }

        onPosWalletCardInput(event) {
            const walletAmount = event.detail;
            this.paymentState.walletAmounts[walletAmount.walletCategory.id] = walletAmount.paymentAmount
        }

        onPosWalletMakePayment(event) {
            const invoicePaymentRegisterScreen = this.paymentRegister.invoicePaymentRegisterScreen;
            const walletInvoicePayments = event.detail;
            // const order = this.props.pos.get_order();

            // We create and add the payment line
            _.each(walletInvoicePayments, (paymentAmount, walletId) => {
                if (paymentAmount) {
                    const paymentMethod = this.props.pos.db.payment_method_by_wallet_id[parseInt(walletId)];
                    // this.paymentRegister._update_invoice_payment_amount(this.paymentState.invoice.id, paymentMethod.id, paymentAmount)
                    const payment = invoicePaymentRegisterScreen._createInvoicePaymentObject({
                        invoice: this.paymentState.invoice,
                        paymentMethod,
                        paymentAmount,
                        invoiceAddress: this.paymentRegister.invoicePaymentRegisterScreen._getPartner()
                    });
                    invoicePaymentRegisterScreen.state.extraPayments.push(payment);
                    store.dispatch('substractWalletAmount', walletId, paymentAmount);
                }
            });

            invoicePaymentRegisterScreen.validatePayments();
        }

    }

    class PayWithWalletButton extends Component {
        // Maybe surchargeAmount won't be needed
        static props = ['pos', 'paymentRegister', 'posPrState', 'surchargeAmount'];

        payWithWalletPopup(event) {
            this.props.pos.gui.show_popup('posPrWalletPayInvoice', {
                title: _t('Pay with wallet'),
                invoice: this.props.posPrState.selectedInvoice,
                paymentRegister: this.props.paymentRegister,
            });
        }
    }

    return {
        LoadWalletWithChangePopupApp,
        LoadWalletWithChangePopupRow,
        PayInvoiceWithWalletPopupApp,
        PayWithWalletButton,
    };

});