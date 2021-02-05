odoo.define('eduweb_utils.Class', function (require) {

    const Class = require('web.Class');

    /**
     * This provides new properties to help us build odoo objects
     *
     * API:
     *
     * @field field: An object with the form:
     * {
     *     <column-name>: {
     *         type: <column-type>,
     *         default: <default-value-if-not-exists>,
     *     },
     *     ...
     * }
     * this will be used by init to build automatically the objects
     *
     * allowed types:
     * integer, float, boolean, char, many2one.
     * The rest of the fields will be just set plain without any special format
     *
     * @field model: This will be used by init to build a object for relation fields
     */
    const EduwebClass = Class.extend({

        /**
         * It converts odoo rpc json to a javascript object
         * @param odooJson A json from a RPC odoo call
         * @public
         */
        init: function (odooJson) {
            if (!odooJson) {
                odooJson = {};
            }

            if (this.fields && typeof (this.fields) == 'object') {
                _.each(this.fields, (fieldDescription) => {
                    const fieldName = fieldDescription.name;
                    if (Object.hasOwnProperty.call(odooJson, fieldName)) {

                        const jsonFieldValue = odooJson[fieldName];

                        switch (fieldDescription.type) {
                            case 'intenger':
                                this[fieldName] = parseInt(jsonFieldValue);
                                break;
                            case 'float':
                                this[fieldName] = parseFloat(jsonFieldValue);
                                break;
                            case 'boolean':
                                this[fieldName] = !!jsonFieldValue;
                                break;
                            case 'char':
                                this[fieldName] = "" + jsonFieldValue;
                                break;
                            case 'many2one':
                                if (jsonFieldValue) {
                                    // It will be a Array if it has the form [id, fields]
                                    // And will be an object if it has {id, ...fields}
                                    if (_.isArray(jsonFieldValue)) {
                                        this[fieldName] = {
                                            id: parseInt(jsonFieldValue[0]),
                                            name: jsonFieldValue[1],
                                        };
                                    } else {
                                        this[fieldName] = jsonFieldValue;
                                    }
                                } else {
                                    this[fieldName] = null;
                                }

                                break;
                            default:
                                this[fieldName] = jsonFieldValue;
                                break;
                        }
                    } else if (fieldDescription.type === 'compute') {
                        Object.defineProperty(this, fieldName, {
                            get: ({
                                'string': this[fieldDescription.method],
                                'function': fieldDescription.method,
                            })[typeof (fieldDescription.method)] || null
                        });
                    } else {
                        this[fieldName] = fieldDescription.default || this._get_default_field_type_value(fieldDescription.type);
                    }
                });
            }
        },

        /**
         * Export a json compatible with odoo rpc methods (create, update, etc...)
         * @returns {JSON}
         */
        export_as_json: function () {
            if (this.fields && typeof (this.fields) == 'object') {
                const exportableJson = {};
                _.each(this.fields, (fieldDescription) => {
                    const fieldName = fieldDescription.name;
                    if (Object.hasOwnProperty.call(this, fieldName)) {
                        switch (fieldDescription.type) {
                            case 'many2one':
                                if (this[fieldName]) {
                                    if (Object.hasOwnProperty.call(this[fieldName], 'id')) {
                                        exportableJson[fieldName] = parseInt(this[fieldName].id);
                                        break;
                                    }
                                }
                                exportableJson[fieldName] = this[fieldName];
                                break;
                            case 'one2many':
                            case 'many2many':
                                exportableJson[fieldName] = [];
                                _.each(this[fieldName], function (fieldRelationMany) {
                                    if (fieldRelationMany.export_as_json) {
                                        exportableJson[fieldName].push(fieldRelationMany.export_as_json());
                                    }
                                });
                                break;
                            default:
                                exportableJson[fieldName] = this[fieldName];
                                break;
                        }
                    }
                });
                return exportableJson;
            }
        },

        /**
         * Odoo get default fields
         * @private
         */
        _get_default_field_type_value: function (fieldType) {
            let defaultValue = null;

            switch (fieldType) {
                case 'char':
                    defaultValue = '';
                    break;
                case 'intenger':
                case 'float':
                    defaultValue = 0;
                    break;
                case 'boolean':
                    defaultValue = false;
                    break;
                case 'selection':
                case 'many2one':
                    defaultValue = null;
                    break;
                case 'many2many':
                case 'one2many':
                    defaultValue = [];
                    break;
            }

            return defaultValue;
        },


    });

    return EduwebClass;

});

odoo.define('eduweb_utils.AutoCompleteInput', function (require) {
    return function (parameters) {
        // Style classes
        const autocompleteCssClass = "autocomplete__container";
        const autocompleteItemCssClass = "autocomplete__container__item";
        const suggestionItemActiveCssClass = "autocomplete__container__item-active";

        // Other variables
        let currentFocusIndex = -1;
        const suggestionContainerEl = document.createElement("DIV");
        let globalCurrentScrollTop = 0;
        this.filterList = [];
        this.filters = parameters.filters || {};
        const inputElement = parameters.inputElement;
        const suggestionList = parameters.suggestionList;

        /**
         * @param {string} filter
         * **/
        this.toggleFilter = (filter) => {
            const index = this.filterList.indexOf(filter)
            if (index === -1) {
                this.filterList.push(filter);
            } else {
                this.filterList.splice(index, 1);
            }
            showSuggestions();
        }

        const applyFilterToSuggestionItemObject = (suggestionItemObject) => {
            let check = true;
            for (let i = 0; i < this.filterList.length; i++) {
                const filterName = this.filterList[i];
                if (Object.hasOwnProperty.call(this.filters, filterName)) {
                    const filter = this.filters[filterName];
                    if (typeof filter === 'function') {
                        check = check && filter(suggestionItemObject);
                    } else {
                        check = check && filter;
                    }
                }
            }
            return check
        }

        const applySearchToSuggestionItemObject = (suggestionItemObject, inputValue) => {
            return suggestionItemObject.search.toLowerCase().includes(inputValue.toLowerCase());
        }

        const closeAllSuggestionLists = function (suggestionListContainerEl) {

            const suggestionContainerElList = document.getElementsByClassName(autocompleteCssClass);

            for (const suggestionContainerEl of suggestionContainerElList) {
                if (suggestionContainerEl !== suggestionListContainerEl) {
                    suggestionContainerEl.parentNode.removeChild(suggestionContainerEl);
                }
            }
        }

        const applySuggestionToInput = event => {
            inputElement.value = event.currentTarget.textContent;
        };

        const createSuggestionElementList = function (inputValue) {
            let suggestionElementList = [];
            for (let i = 0; i < suggestionList.length; i++) {

                const suggestionItemObject = suggestionList[i];

                if (applyFilterToSuggestionItemObject(suggestionItemObject) && applySearchToSuggestionItemObject(suggestionItemObject, inputValue)) {
                    const suggestionItemEl = document.createElement("LI");
                    suggestionItemEl.textContent = suggestionItemObject.label;
                    suggestionItemEl.classList.add(autocompleteItemCssClass);

                    const dataset = suggestionItemObject.dataset;
                    for (const dataKey in dataset) {
                        if (Object.hasOwnProperty.call(dataset, dataKey)) {
                            suggestionItemEl.dataset[dataKey] = dataset[dataKey]
                        }
                    }

                    suggestionItemEl.addEventListener("click", event => {
                        applySuggestionToInput(event);
                        if (suggestionItemObject.onclick && typeof (suggestionItemObject.onclick) === 'function') {
                            suggestionItemObject.onclick(event);
                        }
                    });

                    suggestionElementList.push(suggestionItemEl);
                }
            }

            return suggestionElementList;

        };

        const showSuggestions = event => {
            suggestionContainerEl.innerHTML = '';
            closeAllSuggestionLists();
            const suggestionElementList = createSuggestionElementList(inputElement.value);
            suggestionElementList.forEach(suggestionEl => suggestionContainerEl.appendChild(suggestionEl));

            suggestionContainerEl.classList.add(autocompleteCssClass);
            inputElement.insertAdjacentElement("afterend", suggestionContainerEl);
            suggestionContainerEl.scrollTop = globalCurrentScrollTop;
        };

        inputElement.addEventListener("keydown", e => {
            const suggestionItems = suggestionContainerEl.getElementsByClassName(autocompleteItemCssClass);
            if (e.keyCode === 40) {
                currentFocusIndex++;
                addActive();
            } else if (e.keyCode === 38) {
                currentFocusIndex--;
                addActive();
            } else if (e.keyCode === 13) {
                /*If the ENTER key is pressed, prevent the form from being submitted,*/
                e.preventDefault();
                if (currentFocusIndex > -1) {
                    /*and simulate a click on the "active" item:*/
                    if (suggestionItems) suggestionItems[currentFocusIndex].click();
                    currentFocusIndex = -1;
                }
            }
        });

        const addActive = function () {

            const suggestionItems = suggestionContainerEl.getElementsByClassName(autocompleteItemCssClass);

            if (!suggestionItems) return false;

            for (let suggestionItem of suggestionItems) {
                suggestionItem.classList.remove(suggestionItemActiveCssClass);
            }

            if (currentFocusIndex >= suggestionItems.length) currentFocusIndex = 0;
            if (currentFocusIndex < 0) currentFocusIndex = (suggestionItems.length - 1);

            const minScrollTop = suggestionContainerEl.scrollTop;
            const suggestionItemHeight = suggestionItems[0].offsetHeight;
            const maxScrollTop = suggestionContainerEl.scrollTop + suggestionContainerEl.offsetHeight - suggestionItemHeight;
            const maxScrollHeight = suggestionContainerEl.offsetHeight - suggestionItemHeight;
            const nextScrollTop = (currentFocusIndex) * suggestionItems[0].offsetHeight
            if (nextScrollTop < minScrollTop) {
                suggestionContainerEl.scrollTop = nextScrollTop;
            } else if (nextScrollTop >= maxScrollTop) {
                const newScrollTop = nextScrollTop - maxScrollHeight
                suggestionContainerEl.scrollTop = newScrollTop;
            }
            console.log({
                nextScrollTop,
                suggestionItemHeight,
                maxScrollTop,
                'New top': nextScrollTop - suggestionContainerEl.offsetHeight - suggestionItemHeight
            });
            suggestionItems[currentFocusIndex].classList.add(suggestionItemActiveCssClass);
            globalCurrentScrollTop = suggestionContainerEl.scrollTop;
        }

        const clickOutInput = event => {

            let element = event.target;
            if (element === inputElement && suggestionContainerEl) {
                element = suggestionContainerEl;
            }
            closeAllSuggestionLists(element);

        };

        inputElement.addEventListener("input", showSuggestions);
        inputElement.addEventListener("click", showSuggestions);
        document.addEventListener("click", clickOutInput);
    }
});

odoo.define('eduweb_utils.numbers', require => {

    /**
     *
     * @param {HTMLInputElement|EventTarget} inputNumberEl
     * @param {Number} decimal
     * @returns {number}
     */
    function verifyInputNumber(inputNumberEl, decimal) {

        // store current positions in variables
        const start = inputNumberEl.selectionStart, end = inputNumberEl.selectionEnd;

        // If the user just delete all, we need to reset it to zero
        if (!inputNumberEl.value) {
            inputNumberEl.value = 0;
        }

        let inputNumberElParsedValue = parseFloat(inputNumberEl.value);

        const regexp = new RegExp(`^\\d*\\.?\\d{0,${decimal || 0}}$`);
        if (regexp.test(inputNumberEl.value)) {
            // No negative validation
            if (inputNumberElParsedValue < 0) {
                // We just convert the number to positive, we don't want negative values here
                inputNumberElParsedValue *= -1;
                // inputNumberEl.value = inputNumberElParsedValue;
            }
            inputNumberEl.beforeValue = inputNumberEl.value;
        } else {
            inputNumberEl.value = inputNumberEl.beforeValue || 0;
            inputNumberElParsedValue = parseFloat(inputNumberEl.value);
        }
        // restore from variables...
        inputNumberEl.setSelectionRange(start, end);
        return inputNumberElParsedValue;
    }

    return {
        verifyInputNumber
    }
});

odoo.define('eduweb_utils', function (require) {

    const NumberInput = require('eduweb_utils.NumberInput');
    const EduwebClass = require('eduweb_utils.Class');
    const AutoCompleteInput = require('eduweb_utils.AutoCompleteInput');

    return {
        NumberInput,
        'Class': EduwebClass,
        AutoCompleteInput,
    };
});
