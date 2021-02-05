odoo.define('pos_partner_panel.owl.components', require => {
    "use strict";

    const {Component} = owl;
    const {useState, useDispatch, useStore, useRef} = owl.hooks;
    const store = require('pos_partner_panel.owl.store');
    const AutoCompleteInput = require('eduweb_utils.AutoCompleteInput');

    class PosWalletPartnerScreenComponent extends Component {
        static props = ['pos'];

        state = useState({
            autoCompleteInput: {},
            partner: {}
        })
        partner = useStore(state => state.current_client, {store});

        mounted() {
            super.mounted();
            const partnerSuggestions = []
            _.each(this.props.pos.db.partner_by_id, partner_id => {
                partnerSuggestions.push({
                    search: this.props.pos.db._partner_search_string(partner_id),
                    label: partner_id.name,
                    data: {
                        partner: partner_id
                    },
                    dataset: {
                        'id': partner_id.id,
                    },
                    onclick: event => {
                        this.props.pos.get_order().set_client(partner_id);
                    },
                })
            });

            this.state.autoCompleteInput = new AutoCompleteInput({
                inputElement: this.el.querySelector('.client_selection__input'),
                suggestionList: partnerSuggestions,
                filters: this._getFilters()
            });
        }

        addFilter(filterName, callback) {
            this.state.autoCompleteInput.filters[filterName] = callback;
        }

        removeFilter(filterName) {
            delete this.state.autoCompleteInput.filters[filterName];
        }

        toggleFilter(filterName) {
            this.state.autoCompleteInput.toggleFilter(filterName)
        }

        /**
         * @private
         */
        _getFilters() {
            return {};
        }

    }

    return {
        PosWalletPartnerScreenComponent,
    }

});