odoo.define("eduweb_js_util.init_owl", (require) => {
    /*
    * This is used to init OWL Enviroment in odoo 13
    * */
    const owlQweb = new owl.QWeb();
    owl.Component.env = {qweb: owlQweb};

    const Session = require('web.Session');

    const { qweb } = require('web.core');

    Session.include({
        load_qweb: function (mods) {
            const lock = this.qweb_mutex.exec(() => {

                const cacheId = this.cache_hashes && this.cache_hashes.qweb;
                const route = '/web/webclient/qweb/' + (cacheId ? cacheId : Date.now()) + '?mods=' + mods;

                return $.get(route).then(doc => {
                    if (!doc) {
                        return;
                    }
                    const owlTemplates = [];

                    for (let child of doc.querySelectorAll("templates > [owl]")) {
                        console.log('Loading owl component');
                        child.removeAttribute('owl');
                        owlTemplates.push(child.outerHTML);
                        child.remove();
                    }
                    qweb.add_template(doc);
                    this.owlTemplates = `<templates> ${owlTemplates.join('\n')} </templates>`;

                    console.log(`OwlTemplates: ${this.owlTemplates}`);
                    owlQweb.addTemplates(this.owlTemplates);
                });

            });

            return lock;
        }
    });

});