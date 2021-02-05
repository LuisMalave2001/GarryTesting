odoo.define('adm.application.additional.questions', require => {

    require('web.core');

    function toggleParentListInTextinput() {
            const willParentListInTextinput = $('[name="c_aisj_additional_questions_q1"]:checked').val() === 'list_ideas';
            $('[name="c_aisj_additional_questions_q1_list"]').toggle(willParentListInTextinput);
        }

    $(document).ready(() => {
        toggleParentListInTextinput();
        $('[name="c_aisj_additional_questions_q1"]').on('change', toggleParentListInTextinput);
    });

});