odoo.define('pos_wallet.owl.components', function (require) {


    // OWL
    const {Component} = owl;
    const {useState, useDispatch, useStore, useRef} = owl.hooks;
    const walletServiceDepenency = require('wallet.services.WalletService');

    const {_t} = require("web.core");
    const store = require('pos_wallet.owl.store');
    const {Paymentline} = require('point_of_sale.models');

    const {verifyInputNumber} = require('eduweb_utils.numbers');

    // Payment
    class WalletPaymentCardCompoment extends Component {

        constructor(parent, props) {
            super(parent, props);
            console.log('Constructor WalletPaymentCardCompoment');

            const {walletCategory} = props || {walletCategory: {}};

            this.state = useState({
                id: walletCategory.id,
                name: walletCategory.name,
                payment_amount: 0,
                categoryList: [],
            });

            this.walletCategory = useState(walletCategory);
        }

        walletInput = useRef("walletInput");
        dispatch = useDispatch(store);
        client_wallet_balances = useStore(state => state.client_wallet_balances, {store});

        get matchCategory() {
            const orderCategoryIds = _.chain(this.state.categoryList).map(categ => {
                const categoryIds = this.getCategParents(categ);
                return categoryIds;
            }).reduce((memo, newArray) => memo.concat(newArray), []).value();
            return this.props.walletCategory.is_default_wallet || (orderCategoryIds.indexOf(this.props.walletCategory.category.id) !== -1);
        }

        getCategParents(categ) {
            return (categ.parent ? this.getCategParents(categ.parent) : []).concat([categ.id])
        }

        patched(snapshot) {
            const res = super.patched(snapshot)
            if (!this.matchCategory) {
                const paymentAmount = 0;
                this.state.payment_amount = paymentAmount;
                this.trigger('pos-wallet-card-input', {
                    paymentAmount,
                    walletCategory: this.walletCategory,
                });
            }
            return res
        }

        triggerInputAction(event) {
            const decimals = ((window.posmodel && window.posmodel.currency) ? window.posmodel.currency.decimals : 2) || 2;
            let paymentAmount = verifyInputNumber(this.walletInput.el, decimals);

            if (this.client_wallet_balances[this.state.id] - paymentAmount < -Math.abs(this.props.walletCategory.credit_limit)) {
                paymentAmount = this.client_wallet_balances[this.state.id] - Math.abs(this.props.walletCategory.credit_limit);
            }
            if (this.matchCategory) {
                this.state.payment_amount = paymentAmount;
                this.walletInput.el.value = paymentAmount
                this.trigger('pos-wallet-card-input', {
                    paymentAmount,
                    walletCategory: this.walletCategory,
                });
            } else {
                this.state.payment_amount = 0;
            }
        }
    }

    class WalletPaymentCardListComponent extends Component {
        static props = ["walletCategory", "walletPaymentAmounts"]
        static components = {WalletPaymentCardListComponent, WalletPaymentCardCompoment}

        updateWalletPaymentAmount(walletPayment) {
            const walletPaymentDetail = walletPayment.detail;
            this.props.walletPaymentAmounts[walletPaymentDetail.walletCategory.id] = walletPaymentDetail.paymentAmount;
        }

    }

    class PosWalletPaymentSTComponent extends Component {
        static props = ['pos', 'height', 'categoryList'];
        static components = {WalletPaymentCardListComponent, WalletPaymentCardCompoment}

        spaceTree = useRef('spaceTree');

        constructor(parent, props) {
            super(...arguments);

            const wallets = [];
            // _.each(posWalletsIds, walletId => {
            //     const walletCategory = this.props.pos.chrome.call('WalletService', 'getWalletById', walletId);
            //     wallets.push(walletCategory);
            // });

            const walletDefault = this.props.pos.chrome.call('WalletService', 'getDefaultWalletWithChildren', this.props.pos.company.id);
            this._removeNoPosWalletChildren(walletDefault);
            this.state = useState({
                walletChildren: walletDefault.children,
                walletDefault: walletDefault,
                wallets: wallets,
                walletPaymentAmounts: {},
            });
        }


        willUpdateProps(nextProps) {
            const result = super.willUpdateProps(nextProps);

            if (Object.hasOwnProperty.call(nextProps, 'categoryList')) {
                const categoryList = nextProps.categoryList;
                for (const children in this.__owl__.children) {
                    if (Object.hasOwnProperty.call(this.__owl__.children, children)) {
                        this.__owl__.children[children].state.categoryList = categoryList;
                    }
                }
            }
            return result;
        }

        getOrderWalletPayment() {

            const walletPaymentAmounts = {};

            _.each(this.wallet_cards, wallet_card => {
                if (wallet_card.state.payment_amount) {
                    walletPaymentAmounts[parseInt(wallet_card.state.id)] = wallet_card.state.payment_amount;
                }
            })

            return walletPaymentAmounts;
        }


        payWithWallet() {
            this.trigger('pos-wallet-make-payment', this.state.walletPaymentAmounts);
        }

        _removeNoPosWalletChildren(wallet) {
            const posWalletsIds = this.props.pos.config.wallet_category_ids;
            if (wallet.children) {
                const newChildred = [];
                for (let i = 0; i < wallet.children.length; i++) {
                    const childWallet = wallet.children[i];
                    if (posWalletsIds.indexOf(childWallet.id) !== -1) {
                        newChildred.push(this._removeNoPosWalletChildren(childWallet));
                    }
                }
                wallet.children = newChildred;
            }
            return wallet;
        }

    }

    class PosWalletPaymentScreenComponent extends Component {

        static components = {PosWalletPaymentSTComponent};
        static props = ['pos'];

        wallet_cards = [];
        button_labels = {
            show: _t('Show'),
            hide: _t('Hide'),
        };
        height = 0;
        header_heigth = 150;
        state = useState({
            show: false,
            button_label: this.button_labels.show,
            categoryList: [],
        });

        payWithWallet(orderWalletPayments) {
            const order = this.props.pos.get_order();

            // We create and add the payment line
            _.each(orderWalletPayments.detail || {}, (paymentAmount, walletId) => {
                const paymentMethod = this.props.pos.db.payment_method_by_wallet_id[parseInt(walletId)];
                const newPaymentline = new Paymentline({}, {
                    order: order,
                    payment_method: paymentMethod,
                    pos: this.props.pos
                });
                newPaymentline.set_amount(paymentAmount);
                store.dispatch('substractWalletAmount', walletId, paymentAmount);

                newPaymentline.set_payment_status('done');
                newPaymentline.paid = true;
                newPaymentline.isWalletPayment = true;
                console.log('newPaymentline: ' + newPaymentline)
                order.paymentlines.add(newPaymentline)
            });

            // order.set_wallet_payments(orderWalletPayments);
            this.props.pos.gui.show_screen('payment');
        }

        /**
         * @override
         */
        mounted() {
            super.mounted();
            // const spaceTreeHeight = document.querySelector('.product-list-scroller.touch-scrollable').offsetHeight
            // _.each(this.__owl__.children, child => {
            //     child.resizeSpaceTreeHeight(spaceTreeHeight);
            // });
        }

        /**
         *
         * @param {OwlEvent} event
         */
        toggleShow(event) {
            const forceState = event.detail;
            this.state.show = forceState !== undefined ? !!forceState : !this.state.show;
            this.state.button_label = this.state.show ? this.button_labels.hide : this.button_labels.show;

            if (this.state.show) {
                this.updateCategoryList();
                this.el.classList.remove('payment-wallet-dashboard--hidden');
            } else {
                this.state.categoryList = [];
                this.el.classList.add('payment-wallet-dashboard--hidden');
            }
        }

        updateCategoryList() {
            this.state.categoryList = _.map(this.props.pos.get_order().orderlines.models, ol => ol.product.categ);
        }
    }

    class PosWalletLoadWalletComponent extends Component {
        static props = ['walletPopup', 'pos']

        walletAmount = useRef("walletAmount");
        state = useState({
            paymentAmount: 0,
            walletCategory: 0,
            paymentMethod: 0,
            currentPartner: {},
        });

        triggerInputAction(event) {
            const decimals = ((window.posmodel && window.posmodel.currency) ? window.posmodel.currency.decimals : 2) || 2;
            let paymentAmount = verifyInputNumber(this.walletAmount.el, decimals);
            this.state.paymentAmount = paymentAmount;
            event.currentTarget.value = paymentAmount;
        }

        get formIsValid() {
            return this.state.paymentAmount && this.state.walletCategory && this.state.paymentMethod
        }

    }

    return {
        // Partner Screen
        WalletPaymentCardCompoment,

        // Payment Screen
        PosWalletPaymentSTComponent,
        PosWalletPaymentScreenComponent,
        WalletPaymentCardListComponent,
        PosWalletLoadWalletComponent,
    }
});