from odoo import fields, models, api
from odoo.tools.misc import formatLang
from collections import defaultdict
# from ..util import DefaultOrderedDict
import logging

_logger = logging.getLogger(__name__)


class PayWithWallet(models.TransientModel):
    _name = 'pay.with.wallet'
    _description = 'Pay with wallet...'

    @api.depends("wallet_payment_line_ids")
    def _compute_used_wallet_ids(self):
        for record in self:
            record.used_wallet_ids = record.wallet_payment_line_ids.mapped("wallet_id")

    @api.depends("partner_id")
    def _compute_wallet_ids(self):
        self.ensure_one()
        context = self._context
        active_move_ids = context.get("active_id", False)

        if active_move_ids:
            walletCategoryEnv = self.env["wallet.category"]
            available_wallets = walletCategoryEnv
            move_ids = self.env["account.move"].browse(active_move_ids)
            for move_id in move_ids:
                partner_id = move_id.get_wallet_partner()
                wallet_ids = walletCategoryEnv.search([])

                for wallet_id in wallet_ids:
                    amount_total = walletCategoryEnv.get_wallet_amount(partner_id, wallet_id)

                    if amount_total > -abs(wallet_id.credit_limit):
                        available_wallets += wallet_id

            # family_ids = self.partner_id.family_ids.ids
            self.wallet_ids = available_wallets

    def pay_with_wallet(self):
        self.ensure_one()

        context = self._context
        active_move_ids = context.get("active_ids", False)

        if active_move_ids:

            wallet_payment_line_dict = {wallet_payment_line_id.wallet_id.id: wallet_payment_line_id.amount
                                        for wallet_payment_line_id in self.wallet_payment_line_ids}

            move_ids = self.env["account.move"].browse(active_move_ids)
            for move_id in move_ids:
                move_id.pay_with_wallet(wallet_payment_line_dict)

    @api.onchange('partner_id')
    def onchange_partner(self):
        for record in self:
            record.wallet_payment_line_ids = record._get_default_lines()

    def _get_default_lines(self):
        active_move_ids = self._context.get('active_ids', [])
        if active_move_ids:
            move_id = self.env["account.move"].browse(active_move_ids)[0]
            partner_id = move_id.get_wallet_partner()

            wallet_to_apply = move_id.get_wallet_due_amounts()
            wallet_partner_amounts = {wallet_id.id: wallet_id.get_wallet_amount(partner_id) for wallet_id in
                                      self.env["wallet.category"].search([])}
            wallet_payment_line_ids = self.env["wallet.payment.line"]

            wallet_suggestion_amounts = move_id.calculate_wallet_distribution(wallet_to_apply, wallet_partner_amounts)

            for wallet_id, amount in wallet_suggestion_amounts.items():
                wallet_payment_line_id = self.wallet_payment_line_ids.create({
                    'partner_id': partner_id.id,
                    "wallet_id": wallet_id.id,
                    "amount": amount
                })
                wallet_payment_line_ids += wallet_payment_line_id
            return wallet_payment_line_ids
    
    @api.depends("partner_id")
    def _compute_wallet_balances(self):
        for wizard in self:
            result = ""
            if wizard.partner_id:
                wallet_balances = wizard.partner_id.get_wallet_balances_dict([])
                for wallet_id, amount in wallet_balances.items():
                    wallet = self.env["wallet.category"].browse(wallet_id)
                    result += "<li><strong>%s:</strong> %s %s %s</li>" % (
                        wallet.name,
                        self.env.company.currency_id.symbol if self.env.company.currency_id.position == 'before' else "",
                        formatLang(self.env, amount),
                        self.env.company.currency_id.symbol if self.env.company.currency_id.position == 'after' else "")
            wizard.wallet_balances = "<div><ul>%s</ul></div>" % result

    partner_id = fields.Many2one("res.partner", required=True)
    wallet_ids = fields.Many2many("wallet.category", compute="_compute_wallet_ids")
    used_wallet_ids = fields.Many2many("wallet.category", compute="_compute_used_wallet_ids")
    wallet_payment_line_ids = fields.One2many("wallet.payment.line", "pay_with_wallet_id", string="Wallets", default=_get_default_lines)
    wallet_balances = fields.Html(string="Wallet Balances", compute="_compute_wallet_balances")


class WalletPaymentLine(models.TransientModel):
    _name = "wallet.payment.line"

    @api.depends("wallet_id", "amount")
    def _compute_partner_amount(self):
        for payment_line in self:
            payment_line.partner_amount = payment_line.wallet_id.get_wallet_amount(payment_line.partner_id) - payment_line.amount

    pay_with_wallet_id = fields.Many2one("pay.with.wallet")
    wallet_id = fields.Many2one("wallet.category", required=True)
    amount = fields.Float()
    partner_id = fields.Many2one("res.partner")
    partner_amount = fields.Float("Partner amount", readonly=True, compute="_compute_partner_amount")