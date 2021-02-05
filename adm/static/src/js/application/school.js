odoo.define('adm.application.school', require => {

    require('web.core');

    function removeNewSchool(event) {
        $(event.currentTarget).closest('[data-adm-rel]').remove();
    }

    function appendNewSchool(event) {
        const $clonedNewSchoolTemplate = $(document.getElementById('template_school')).clone(true);

        // We remove the style display none
        $clonedNewSchoolTemplate.removeAttr('style');

        const schoolList = document.getElementById('school_list');
        const newMany2manyRev = document.createElement('DIV');
        newMany2manyRev.dataset.admRel = "rel";
        $clonedNewSchoolTemplate.appendTo(newMany2manyRev);
        // newMany2manyRev.appendChild(clonedNewSchoolTemplate)
        schoolList.appendChild(newMany2manyRev);
    }

    $(document).ready(() => {
        $('.add-school').on('click', appendNewSchool);
        $('.remove-school').on('click', removeNewSchool);
    });

});