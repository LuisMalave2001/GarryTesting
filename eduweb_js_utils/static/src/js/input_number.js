odoo.define('eduweb_utils.NumberInput', function (require) {

    /**
     * Format an input to numeric
     * @param element
     * @param opts
     * @constructor
     */
    function NumberInput(element, opts) {
        if (!opts) {
            opts = {};
        }

        let defaultOpts = {
            "decimal_limit": opts.decimal_limit || 0
        };

        if (element.tagName === 'INPUT') {

            element.addEventListener('keydown', event => {
                return event.key.match("(\\d|\\.|,|Arrow|Backspace|Delete|Tab)") !== null;
            });

            element.addEventListener('input', event => {
                let elementType = element.type;
                element.type = "text";

                let inputValue = parseFloat(element.value);
                let selectionPositionStart = element.selectionStart;
                let selectionPositionEnd = element.selectionEnd;

                let inputDecimalPart = (inputValue % 1).toFixed(defaultOpts.decimal_limit).replace("0.", "");
                element.value = Math.trunc(inputValue) + "." + inputDecimalPart;

                element.type = elementType;
                element.setSelectionRange(selectionPositionStart, selectionPositionEnd);
            });
        }

        if (!element.value.match("^\\d+\\.?\\d+$")) {
            element.value = 0;
        }
        element.dispatchEvent(new Event("input"));
    }
    
    return NumberInput;
});
