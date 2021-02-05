odoo.define("pos_pr.owl.init", function (require) {
    /*
    * This is used to init all OWL stuff like templates...
    * */

    require('eduweb_js_util.init_owl');

    async function loadTemplate() {
        try {
            const templates = await owl.utils.loadFile('/pos_pr/static/src/xml/owl/screens.xml');


            owl.Component.env.qweb.addTemplates(templates);
            console.log('Templates loaded successfully!');
        } catch (e) {
            console.error(`Couldn't load templates correctly`);
            throw e;
        }
    }

    return loadTemplate();
});