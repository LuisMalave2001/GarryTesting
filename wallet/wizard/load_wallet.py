
from odoo import fields, models, api, _
import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LoadWallet(models.TransientModel):
    _name = 'load.wallet'
    _description = 'Load wallet...'

    def _get_company_currency(self):
        for record in self:
            record.currency_id = self.env.company.currency_id

    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True,
                                  string="Currency", help='Utility field to express amount currency')

    wallet_id = fields.Many2one("wallet.category", "Wallet")
    amount = fields.Monetary("Amount")
    max_amount = fields.Monetary(compute="_compute_max_amount", store=True, readonly=True)
    current_amount = fields.Monetary(string="Current Amount", compute="_compute_current_amount")

    # For some reason, payment_ids is not required ._.
    payment_ids = fields.Many2many("account.payment", required=True)
    wallet_category_id = fields.Many2one("wallet.category", "Wallet Category")
    wallet_journal_category_id = fields.Many2one(related="wallet_category_id.journal_category_id")

    partner_id = fields.Many2one("res.partner", "Partner")
    payment_partner_id = fields.Many2one("res.partner", compute="compute_payment_partner_id", store=True)

    @api.depends('partner_id')
    @api.onchange('partner_id')
    def compute_payment_partner_id(self):
        for load_wallet in self:
            load_wallet.payment_partner_id = load_wallet.partner_id

    @api.constrains("amount")
    def _check_amount(self):
        for record in self:
            if record.amount > record.max_amount:
                raise ValidationError(_("Amount cannot be greather than max amount"))
            if record.amount < 0:
                raise ValidationError(_("Amount cannot be neggative"))

    @api.onchange("wallet_id")
    def _remove_payments_without_selected_wallet_id(self):
        wallet_id = self.wallet_id if self.wallet_id != self.wallet_id.default_wallet_category_id else False
        self.payment_ids = self.payment_ids.filtered(lambda payment: payment.wallet_id == self.wallet_id or not payment.wallet_id)

    @api.depends('payment_ids')
    def _compute_max_amount(self):
        for record in self:
            record.max_amount = sum(record.payment_ids.mapped("unpaid_amount"))

    @api.depends('amount', 'payment_ids')
    def _onchange_amount(self):
        for record in self:

            max_amount = 0.0

            if record.payment_ids:
                max_amount = sum(record.payment_ids.mapped(lambda payment: payment.amount))

            if record.amount > max_amount:
                record.amount = max_amount

    @api.model
    def create(self, vals_list):
        load_wallet_id = super().create(vals_list)
        if not load_wallet_id.payment_ids:
            raise ValidationError(_("Please, add at least one payment"))
        else:
            draft_payment_ids = load_wallet_id.payment_ids.filtered(lambda payment: payment.state == 'draft')
            draft_payment_ids.post()

        return load_wallet_id

    def load_wallet(self):
        self.ensure_one()
        context = self.env.context
        partner_ids = context.get("active_ids", False)

        if partner_ids:
            if self.payment_ids:
                resPartner = self.env["res.partner"]
                load_wallet_with_payment_params = self._build_load_wallet_with_payment_params()
                resPartner.browse(partner_ids).load_wallet_with_payments(**load_wallet_with_payment_params)

    def _build_load_wallet_with_payment_params(self):
        return {
            'payment_ids': self.payment_ids.ids,
            'wallet_id': self.wallet_id.id,
            'amount': self.amount,
            'partner_id': self.payment_partner_id
            }

    @api.depends("wallet_id", "partner_id")
    def _compute_current_amount(self):
        for wizard in self:
            result = 0
            if wizard.wallet_id and wizard.partner_id:
                wallet_balances = wizard.partner_id.get_wallet_balances_dict([wizard.wallet_id.id])
                result = wallet_balances[wizard.wallet_id.id]
            wizard.current_amount = result