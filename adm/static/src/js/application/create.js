odoo.define('adm.application.create', require => {
    "use strict";

    require('web.core');
    // const session = require('web.session');
    // const rpc = require('web.rpc');
    //
    // const user_partner = await rpc.query({
    //     model: 'res.users',
    //     method: 'read',
    //     args: [[session.user_id], ['partner_id']],
    // });
    // const partner_id = user_partner[0].partner_id[0];
    // let partner = await rpc.query({
    //     model: 'res.partner',
    //     method: 'read',
    //     args: [[partner_id], ['family_ids']],
    // });
    // partner = partner[0];
    // console.log(partner.family_ids);

    $(document).ready(() => {
        // const $selectModal = $(document.getElementById('family_select_modal'));
        // $('.o_adm_family_select_item').on('click', event => {
        //     const familyItemEl = event.currentTarget;
        //     $('input[name="family_id"]').val(familyItemEl.dataset.familyId);
        //     $selectModal.modal('hide');
        // });
        // $selectModal.modal({backdrop: 'static', keyboard: false});
    });
});