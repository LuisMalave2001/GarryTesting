odoo.define('adm.application.signature', require => {
    "use strict";

    require('web.core');
    let signaturePad;
    function createNewSignature() {
        const signaturePadEl = document.getElementById('signature-pad');
        const spingLagLoader = document.getElementById('js_spin_lag_loader');

        if (spingLagLoader) {
            spingLagLoader.style.removeProperty('display');
        }

        if (signaturePadEl) {
            signaturePad = new SignaturePad(signaturePadEl, {
                backgroundColor: 'rgba(255, 255, 255, 0)',
                penColor: 'rgb(0, 0, 0)'
            });
            if (spingLagLoader) {
                spingLagLoader.style.setProperty('display', 'none', 'important');
            }
        }
    }

    $(document).ready(() => {
        createNewSignature();
        if (signaturePad) {
            const signatureImageUrl = $('input[name="signature_attach_url"]').val();
            if (signatureImageUrl) {
                signaturePad.fromDataURL('data:image/png;base64,' + signatureImageUrl);
            }
        }
        const clearSignature = document.getElementById('clear_signature');
        if (clearSignature) {
            clearSignature.addEventListener('click', createNewSignature);
        }
        $('.js_submit_json').on('click', event => {
            if (signaturePad) {
                let dataURL = signaturePad.toDataURL();
                dataURL = dataURL.replace('data:image/png;base64,','');
                $('input[name="signature_attach_url"]').val(dataURL);
            }
        });
    })

});