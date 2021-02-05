// odoo.define('pos_school_wallet.pos_model', function (require) {
//
//     const models = require("point_of_sale.models");
//     // const rpc = require('web.rpc');
//
//     // const core = require("web.core");
//     // const _t = core._t;
//     // const store = require('pos_wallet.owl.store');
//
//     require('pos_wallet.pos_wallet_methods');
//
//     // models.load_fields('pos.session', ['pos_wallet_load_ids']);
//     // models.load_fields('res.company', ['city', 'street', 'parent_id']);
//
//     // const pendingWalletLoads = this.pos.db.load('pending_wallets_load', []);
//     // const pendingWalletLoads =
//     // const pendingWalletPayments = this.pos.db.load('pending_wallets_payments', []);
//
//     const PosModelSuper = models.PosModel;
//     models.PosModel = models.PosModel.extend({
//         _build_pos_wallet_wallet_load_params: function (params) {
//             let paymentBuiltParams = PosModelSuper.prototype._build_pos_wallet_wallet_load_params.apply(this, arguments);
//
//             if (params.student.id) {
//                 paymentBuiltParams.student_id = params.student.id
//             }
//
//             if (params.family.id) {
//                 paymentBuiltParams.family_id = params.family.id
//             }
//
//             return paymentBuiltParams;
//         }
//     })
//
// });