odoo.define("school_base.setting", function(require){

    var BaseSetting = require("base.settings");
    var core = require('web.core');

    var BaseSettingRenderer = BaseSetting.Renderer;
    var QWeb = core.qweb;
    var _t = core._t;

    console.log(BaseSettingRenderer);

    let SchoolBaseSettingRenderer = BaseSettingRenderer.include({

        confirmChange: function(){
            var self = this;
            return this._super.apply(this, arguments).then(function(){
                if (!self.$('.school_base_dirty_warning').length){
                    var $button = self.$('button.setting-block-editing');
                    if ($button){
                        $button.prop("disabled", true)
                        .append($('<div/>', {text: _t("You need to save the changes first"),
                                              class: 'text-muted ml-2 school_base_dirty_warning'}))
                    }
                }
            })
        }

    })

    return SchoolBaseSettingRenderer;

});