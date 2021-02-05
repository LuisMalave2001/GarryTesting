odoo.define('pos_pr_school.owl.components', require => {
    "use strict";

    const {PosPRScreen} = require('pos_pr.owl.components');
    const {useState, Component, patch} = owl;
    const {useRef} = owl.hooks;

    patch(PosPRScreen, {

        setup() {
            this._super();
            Object.defineProperty(this, 'studentList', {get: this._getStudentList});
            Object.defineProperty(this, 'invoiceAddressList', {get: this._getInvoiceAddressList});
            Object.defineProperty(this, 'invoicesPartnerList', {get: this._getInvoicesPartnerList});

            this.schoolState = useState({
                filterStudentsIds: [],
                filterPartnerIds: [],
                selectedInvoiceAddress: 0,
            });

            this.selectInvoiceAddressRef = useRef("selectInvoiceAddressRef");

        },

        patched() {
            this._super();
            // If they are different, that means that the partner has changed
            if (this.state.partner.person_type === 'student') {
                this.schoolState.selectedInvoiceAddress = this.invoiceAddressList.length ? this.invoiceAddressList[0] : {};
            }
        },

        selectInvoiceAddress() {
            const selectInvoiceAddressId = parseInt(this.selectInvoiceAddressRef.el.value) || 0
            this.schoolState.selectedInvoiceAddress = _.find(this.invoiceAddressList, invAddress => invAddress.id === selectInvoiceAddressId);
        },

        toggleFilter(event) {

            const button = event.currentTarget;
            button.classList.toggle('toggle-screen-filter-button--active')

            this.state.showScreen = !this.state.showScreen;
        },

        _buildPaymentGroupValues() {
            const paymentGroupsValues = this._super(...arguments);

            if (this.state.partner.person_type === 'student') {
                paymentGroupsValues.partner_id = this.schoolState.selectedInvoiceAddress;
            }

            return paymentGroupsValues;
        },

        _createInvoicePaymentObject(properties) {
            const invoicePayment = this._super(...arguments);

            invoicePayment.student_id = properties.invoice.student_id && properties.invoice.student_id.id;
            invoicePayment.family_id = properties.invoice.family_id && properties.invoice.family_id.id;

            return invoicePayment;
        },

        _createGenericSurcharge() {
            const surcharge = this._super();

            if (this.state.partner.person_type === 'student') {
                surcharge.partner_id = this.schoolState.selectedInvoiceAddress;
            }

            return surcharge;
        },

        _getPartner() {
            return this.schoolState.selectedInvoiceAddress || this.state.partner;
        },

        _getFilteredInvoiceList() {
            let filteredInvoiceList = this._super();

            filteredInvoiceList = filteredInvoiceList.filter(invoice =>
                (!this.schoolState.filterStudentsIds.length || _.indexOf(this.schoolState.filterStudentsIds, invoice.student_id.id) !== -1)
                && (!this.schoolState.filterPartnerIds.length || _.indexOf(this.schoolState.filterPartnerIds, invoice.partner_id.id) !== -1)
            )
            console.log("_getFilteredInvoiceList");

            return filteredInvoiceList
        },

        _getInvoiceList() {
            const invoiceList = this._super();

            const schoolInvoiceList = _.filter(this.props.pos.db.due_invoices, invoice =>
                invoice.amount_residual > 0
                && (
                    (invoice.student_id && invoice.student_id.id === this.state.partner.id)
                    || (invoice.family_id && invoice.family_id.id === this.state.partner.id)
                )
            )

            invoiceList.push(...schoolInvoiceList);

            return invoiceList;
        },

        _getStudentList() {
            const invoiceList = this.invoiceList;
            if (invoiceList) {
                return _.chain(invoiceList).map(invoice => invoice.student_id).uniq(false, student => student.id).value();
            } else {
                return [];
            }
        },

        _getInvoiceAddressList() {
            return this.state.partner ? _.map(this.state.partner.student_invoice_address_ids, partnerId => this.props.pos.db.partner_by_id[partnerId]) : [];
        },

        _getInvoicesPartnerList() {
            const invoiceList = this.invoiceList;
            if (invoiceList) {
                return _.chain(invoiceList).map(invoice => invoice.partner_id).uniq(false, partner => partner.id).value();
            } else {
                return [];
            }
        }

    });

    class PosPRScreenFilter extends Component {
        static props = ['studentList', 'invoiceAddressList', 'posPrState', 'posPrSchoolState'];

        /**
         * @param {EventTarget} checkboxElement
         * @param {HTMLInputElement} checkboxElement
         * @param {String} propsListName
         * @param value
         * @private
         */
        _toggleListFilterWithCheckbox(checkboxElement, propsListName, value) {
            const auxList = Array.from(this.props.posPrSchoolState[propsListName]);
            if (checkboxElement.checked) {
                auxList.push(value);
            } else {
                const index = _.indexOf(auxList, value);
                if (index > -1) {
                    auxList.splice(index, 1);
                }
            }
            this.props.posPrSchoolState[propsListName] = auxList;
        }

        toggleStudentFilter(studentId, event) {
            this._toggleListFilterWithCheckbox(event.currentTarget, 'filterStudentsIds', studentId);
        }

        togglePartnerFilter(invoiceAddressId, event) {
            this._toggleListFilterWithCheckbox(event.currentTarget, 'filterPartnerIds', invoiceAddressId);
        }
    }

    // Asign in the class
    PosPRScreen.components.PosPRScreenFilter = PosPRScreenFilter;

    return {
        PosPRScreenFilter,
    }


});