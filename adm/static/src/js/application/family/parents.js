odoo.define('adm.family.parents', require => {
    "use strict";

    require('web.core');

    function toggleParentForm(el, isChecked) {
        const $container =  $(el).closest('.container');
        $container.find('.js_existing_selection').toggle(isChecked).find('input, select').prop('disabled', !isChecked);
        $container.find('.js_invisible_existing').toggle(!isChecked)
                  .find('input, select').prop('disabled', isChecked);
    }

    $(document).ready(() => {

        $('input.js_existing:checkbox').on('change', (event) => {
            const el = event.currentTarget;
            const isChecked = !!el.checked;
            toggleParentForm(el, isChecked);
        });

        $('.js_clean_parent').on('click', event => {
            const $target = $(event.currentTarget.dataset.target);
            $target.find('input:visible').val([]);

            const elCheckbox = $target.find('input.js_existing[type="checkbox"]');
            if (elCheckbox) {
                toggleParentForm(elCheckbox, false);
            }

            $target.find('[data-adm-field="partner_2"]').find('input:hidden').remove();
            $target.find('img').attr('src', '/adm/static/img/contact_photo_placeholder.png');
        });

    });
})