odoo.define("pos_school_wallet.components", function (require) {

    const {PosWalletLoadWalletComponent, LoadWalletPopup} = require('pos_wallet.popups');
    const {useState, Component, patch} = owl;

    patch(PosWalletLoadWalletComponent, {
        setup() {
            this._super();
            Object.defineProperty(this, 'invoiceAddressList', {get: this._getInvoiceAddressList});
            Object.defineProperty(this, 'familyRelatedByInvoiceAddressList', {get: this._getFamilyRelatedByInvoiceAddressList});

            this.schoolState = useState({
                selectedInvoiceAddress: 0,
                selectedFamily: 0,
            });
        },
        _getInvoiceAddressList() {
            const self = this;
            return this.props.pos.get_client() ? _.map(this.props.pos.get_client().student_invoice_address_ids, partnerId => self.props.pos.db.partner_by_id[partnerId]) : [];
        },
        _getFamilyRelatedByInvoiceAddressList() {
            const self = this;
            return this.schoolState.selectedInvoiceAddress ? _.chain(this.schoolState.selectedInvoiceAddress.related_families_by_inv_address_ids)
                .filter(familyId => self.props.pos.get_client().family_ids.indexOf(familyId) !== -1)
                .map(familyId => self.props.pos.db.partner_by_id[familyId]).value() : [];
        },
        selectInvoiceAddress(event) {
            const selectInvoiceAddressId = parseInt(event.currentTarget.value) || 0;
            this.schoolState.selectedInvoiceAddress = _.find(this.invoiceAddressList, invAddress => invAddress.id === selectInvoiceAddressId);
            this.schoolState.selectedFamily = this.familyRelatedByInvoiceAddressList.length ? this.familyRelatedByInvoiceAddressList[0] : {};
        },
        selectFamily(event) {
            const selectedFamilyId = parseInt(event.currentTarget.value) || 0;
            this.schoolState.selectedFamily = _.find(this.familyRelatedByInvoiceAddressList, family => family.id === selectedFamilyId);
        }
    });

    LoadWalletPopup.include({
        show: function () {
            if (this.pos.get_client()) {

                const invoiceAddressList = this.posWalletLoadWalletComponent.invoiceAddressList;
                this.posWalletLoadWalletComponent.schoolState.selectedInvoiceAddress = invoiceAddressList.length ? invoiceAddressList[0] : {};

                const familyRelatedByInvoiceAddressList = this.posWalletLoadWalletComponent.familyRelatedByInvoiceAddressList;
                this.posWalletLoadWalletComponent.schoolState.selectedFamily = familyRelatedByInvoiceAddressList.length ? familyRelatedByInvoiceAddressList[0] : {};
            }
            this._super.apply(this, arguments);
        },

        _build_load_wallet_options: function () {

            let options = this._super.apply(this, arguments);

            if (this.pos.get_client() && this.pos.get_client().person_type === 'student') {

                options = _.extend({}, options, {
                    student: this.pos.get_client(),
                    family: this.posWalletLoadWalletComponent.schoolState.selectedFamily,
                });

                options.partner_id = this.posWalletLoadWalletComponent.schoolState.selectedInvoiceAddress.id
            }
            return options
        }
    });
});
