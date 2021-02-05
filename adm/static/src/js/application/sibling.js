odoo.define('adm.application.sibling', require => {

    require('web.core');

    let counter = 0;

    function removeNewSibling(event) {
        $(event.currentTarget).closest('[data-adm-rel]').remove();
    }

    function appendNewSibling(event) {
        counter--;
        const $clonedNewSiblingTemplate = $(document.getElementById('template_sibling')).clone();

        const $buttonToggleCollapse = $clonedNewSiblingTemplate.find('[data-toggle="collapse"]')
        $buttonToggleCollapse[0].dataset.target = $buttonToggleCollapse[0].dataset.target + counter.toString();

        const $divCollapse = $clonedNewSiblingTemplate.find('.collapse');
        $divCollapse[0].id = $divCollapse[0].id + counter.toString();

        $clonedNewSiblingTemplate.find('input[type="radio"]').each((i, elIputRadio) => {
             elIputRadio.name = elIputRadio.name + counter.toString();
        });
        // We remove the style display none
        $clonedNewSiblingTemplate.removeAttr('style');

        const siblingList = document.getElementById('sibling_list');
        const newMany2manyRev = document.createElement('DIV');
        newMany2manyRev.dataset.admRel = "rel";
        $clonedNewSiblingTemplate.appendTo(newMany2manyRev);
        $clonedNewSiblingTemplate.find('.remove-sibling').on('click', removeNewSibling);
        // newMany2manyRev.appendChild(clonedNewSiblingTemplate)
        siblingList.appendChild(newMany2manyRev);
    }

    $(document).ready(() => {
        $('.add-sibling').on('click', appendNewSibling);
        $('.remove-sibling').on('click', removeNewSibling);
    });

});