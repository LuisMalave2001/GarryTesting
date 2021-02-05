odoo.define('adm.application.common', require => {
    "use strict";

    require('web.core');
    const utils = require('web.utils')

    async function buildAdmJSONObject(rootEl) {
        let auxJson = {};

        async function getValueDependingOnType($el) {
            if ($el.is(':file')) {
                const fileFromEl = $el[0].files[0];
                const urlEncodedFile = await utils.getDataURLFromFile(fileFromEl);
                const base64EncodedFile = urlEncodedFile.split(',')[1];
                if (($el.data('admFieldType') || '').toUpperCase() === 'ATTACHMENT') {
                    return {
                        'content_type': fileFromEl.type,
                        'name': fileFromEl.name,
                        'base64_encoded_file': base64EncodedFile,
                    }
                } else {
                    return base64EncodedFile;
                }
            }
            let val;

            switch (($el.data('admFieldType') || '').toUpperCase()) {
                case 'INTEGER':
                case 'MANY2MANY_CHECKBOX':
                    val = parseInt($el.val());
                    break;
                case 'FLOAT':
                    val = parseFloat($el.val());
                    break;
                case 'BOOLEAN':
                    val = !!$el.is(':checked');
                    break;
                default:
                    val = $el.val();
                    break;
            }

            return val;

        }

        function cloneChildren($el) {
            const clonedEl = $el.clone();
            const auxDiv = document.createElement("DIV");
            clonedEl.children().appendTo(auxDiv);
            return auxDiv;
        }

        const firstFields = $(rootEl).find('[data-adm-field]:not([data-adm-field] [data-adm-field])');
        for (let i = 0; i < firstFields.length; ++i) {
            const el = firstFields[i];
            const $el = $(el);
            if ((($el.is(':radio') || $el.is(':checkbox:not([data-adm-field-type=BOOLEAN])')) && !$el.is(':checked'))
                || $el.prop('disabled')
                || ($el.is(':file') && (!el.files || !el.files.length))) {
                continue;
            }

            const fieldName = $el.data('admField');
            const fieldType = ($(el).data('admFieldType') || '').toUpperCase();
            switch (fieldType) {
                case 'MANY2MANY':
                case 'ONE2MANY':
                    const auxDivMany2many = cloneChildren($el);

                    auxJson[fieldName] = [];
                    const $elRelList = $(auxDivMany2many).find('[data-adm-rel]:not([data-adm-rel] [data-adm-rel])');
                    for (let j = 0; j < $elRelList.length; j++) {
                        const elRel = $elRelList[j];
                        const $elRel = $(elRel);
                        const rootResetedRel = cloneChildren($elRel);
                        const relResult = await buildAdmJSONObject(rootResetedRel)
                        auxJson[fieldName].push(relResult);
                    }
                    break;
                case 'MANY2ONE':
                    const auxDivMany2one = cloneChildren($el);
                    const many2manyJSON = await buildAdmJSONObject(auxDivMany2one)
                    if (!auxJson[fieldName]) {
                        auxJson[fieldName] = await buildAdmJSONObject(auxDivMany2one);
                    } else {
                        auxJson[fieldName] = {
                            ...auxJson[fieldName],
                            ...many2manyJSON,
                        };
                    }
                    break;
                case 'MANY2MANY_CHECKBOX':
                    auxJson[fieldName] = auxJson[fieldName] || [];
                    const elValue = await getValueDependingOnType($el);
                    auxJson[fieldName].push({id: elValue});
                    break;
                default:
                    auxJson[fieldName] = await getValueDependingOnType($el);
                    break;
            }
        }

        return auxJson;
    }

    function sendJson(event) {
        const btnSave = event.currentTarget;
        const nextUrlPage = btnSave.dataset.nextUrl;
        const mainRoot = $('[data-adm-model-fields="1"]');
        buildAdmJSONObject(mainRoot).then(jsonToSend => {
            console.log(jsonToSend);
            const applicationId = $('meta[name="_application_id"]').attr("value");//$('meta[name="_application_id"]').val();

            $.ajax({
                url: '/admission/applications/' + applicationId + '/',
                method: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify(jsonToSend),
                csrf_token: odoo.csrf_token,
                beforeSend: () => {
                    $(document.getElementById('adm_loader')).show();
                },
                success: () => {
                    if (nextUrlPage) {
                        window.location.href = nextUrlPage;
                    } else {
                        window.location.reload();
                    }
                },
                error: () => {
                    $(document.getElementById('adm_loader')).hide();
                },
            })
        });
    }

    function getValueFromGenericInput($el) {
        var value = $el;
        var type = value.attr("type");

        if (type && type.toLowerCase() == 'radio') {
            value = value.filter(":checked").val();
        } else {
            value = value.val();
        }
        return value;
    }

    $(document).ready(() => {
        $('.js_show_when_input').each((i, el) => {
            const cssQueryTarget = el.dataset.target;
            const isValue = el.dataset.isValue;

            const toggleShow = () => {
                const willShow = getValueFromGenericInput($(cssQueryTarget)) == isValue;
                $(el).toggle(willShow);
            }
            $(cssQueryTarget).on('change', toggleShow);
            toggleShow();
        });
        $('.form-upload').each((i, el) => {
            const $el = $(el);
            const inputFile = $el.find('input[type=file]');
            const inputSpanLabel = $el.find('.js_input_file_label');
            inputFile.on('change', (event) => {
                inputSpanLabel.text(event.currentTarget.files[0].name);
            });
        });
        $('.js_submit_json').on('click', sendJson);
    });

})
;