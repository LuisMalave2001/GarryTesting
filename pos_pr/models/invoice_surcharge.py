from odoo import models, fields, api, _
from odoo.addons import account


class InvoicePaymentSurcharge(models.Model):
    _name = "pos_pr.invoice.surcharge"

    move_ids = fields.Many2many("account.move")
    surcharge_move_id = fields.Many2one("account.move")
    payment_ids = fields.Many2many("pos_pr.invoice.payment")
    amount = fields.Float("Amount")
    pos_session_id = fields.Many2one("pos.session")
    free_of_surcharge = fields.Float("Free of surcharge", default=0)
    partner_id = fields.Many2one('res.partner', string=_("Customer"), store=True, compute='_compute_partner_id')

    date = fields.Date()

    @api.depends('move_ids')
    def _compute_partner_id(self):
        for surcharge_id in self:
            partner_id = surcharge_id.mapped('move_ids.partner_id')
            if partner_id:
                partner_id.ensure_one()
                surcharge_id.partner_id = partner_id

    @api.model
    def create(self, vals_list):
        surcharge_ids = super().create(vals_list)
        surcharge_ids.refresh_surcharge_to_invoices()
        return surcharge_ids

    def apply_surcharge(self):
        for surcharge_id in self.filtered('move_ids'):
            if surcharge_id.amount > 0:
                surcharge_product_id = self.env["ir.config_parameter"].get_param("pos_pr.surcharge_product_id", False)

                if surcharge_product_id:
                    surcharge_product_id = int(surcharge_product_id)

                surcharge_move_id = surcharge_id.create_invoice(surcharge_product_id)
                surcharge_move_id.post()

                surcharge_id.surcharge_move_id = surcharge_move_id

                if surcharge_id.free_of_surcharge:
                    surcharge_id.create_credit_note(surcharge_product_id)

                surcharge_id.apply_payments_to_surcharge()

    def create_credit_note(self, surcharge_product_id: int):
        self.ensure_one()
        credit_note_id = self.env["account.move"].create({
            "type": "out_refund",
            "partner_id": self.surcharge_move_id.partner_id.id,
            "journal_id": self.surcharge_move_id.journal_id.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": surcharge_product_id,
                "price_unit": self.free_of_surcharge,
                "quantity": 1,
            })],
        })
        credit_note_id.post()
        (credit_note_id | self.surcharge_move_id).get_receivable_line_ids().reconcile()

    def create_invoice(self, surcharge_product_id: int):
        self.ensure_one()
        partner_id = self.move_ids.mapped("partner_id").ensure_one()
        surcharge_move_id = self.env["account.move"].create({
            "type": "out_invoice",
            "partner_id": partner_id.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": surcharge_product_id,
                "price_unit": self.amount + self.free_of_surcharge,
                "quantity": 1,
            })],
        })
        return surcharge_move_id

    def apply_payments_to_surcharge(self):
        self.ensure_one()
        self.payment_ids.write({"move_id": self.surcharge_move_id.id})

    def refresh_surcharge_to_invoices(self):
        for surcharge_id in self:
            move_ids = surcharge_id.move_ids.sorted("invoice_date_due")
            move_amount = surcharge_id.amount + surcharge_id.free_of_surcharge
            for move_id in move_ids:
                amount_to_remove = min(move_id.surcharge_amount, move_amount)
                move_id.surcharge_amount -= amount_to_remove
                move_amount -= amount_to_remove
                if move_amount <= 0:
                    break
