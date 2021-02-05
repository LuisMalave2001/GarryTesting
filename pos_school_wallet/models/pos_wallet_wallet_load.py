# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class PosWalletWalletLoad(models.Model):
    _inherit = 'pos_wallet.wallet.load'

    def _build_load_wallet_with_line_ids_params(self, line_ids, wallet_id, amount):
        load_wallet_with_line_ids_params = super(PosWalletWalletLoad, self)._build_load_wallet_with_line_ids_params(line_ids, wallet_id, amount)

        load_wallet_with_line_ids_params.update({
            'partner_id': self.partner_id,
            'move_params': {
                'student_id': self.student_id.id,
                'family_id': self.family_id.id,
                },
            })

        return load_wallet_with_line_ids_params

    def _get_load_partner(self):
        return (self.mapped('student_id')
                or self.mapped('family_id')
                or super(PosWalletWalletLoad, self)._get_load_partner())

    def _load_with_lines(self, wallet_line_ids):
        partner_id = self._get_load_partner()
        responsible_partner_ids = self.mapped('partner_id')
        wallet_ids = wallet_line_ids.mapped('pos_wallet_category_id')

        for responsible_partner_id in responsible_partner_ids:
            responsible_load_ids = self.filtered(lambda load: load.partner_id == responsible_partner_id)
            family_ids = responsible_load_ids.mapped('family_id')
            for wallet_category_id in wallet_ids:
                line_ids = wallet_line_ids.filtered(lambda line_id: line_id.pos_wallet_category_id == wallet_category_id and line_id.partner_id == responsible_partner_id)
                if line_ids:
                    if family_ids:
                        for family_id in family_ids:
                            amount = sum(responsible_load_ids.filtered(lambda wallet_load_id: wallet_load_id.wallet_category_id == wallet_category_id).mapped('amount'))
                            loads_filtered_by_family = responsible_load_ids.filtered(lambda load: load.family_id == family_id)
                            load_wallet_with_line_ids_params = loads_filtered_by_family._build_load_wallet_with_line_ids_params(line_ids, wallet_category_id, amount)
                            partner_id.load_wallet_with_line_ids(**load_wallet_with_line_ids_params)
                    else:
                        for wallet_category_id in wallet_ids:
                            amount = sum(responsible_load_ids.filtered(lambda wallet_load_id: wallet_load_id.wallet_category_id == wallet_category_id).mapped('amount'))
                            load_wallet_with_line_ids_params = responsible_load_ids._build_load_wallet_with_line_ids_params(line_ids, wallet_category_id, amount)
                            partner_id.load_wallet_with_line_ids(**load_wallet_with_line_ids_params)


