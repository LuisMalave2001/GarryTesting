from odoo import fields, models, api
from odoo.tools import float_round


class WalletCategory(models.Model):
    _name = 'wallet.category'
    _description = 'Wallet categories'

    name = fields.Char(required=True)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    default_wallet_category_id = fields.Many2one('wallet.category', related='company_id.default_wallet_category_id', store=True)
    is_default_wallet = fields.Boolean(compute='_compute_is_default_wallet', store=True)

    journal_category_id = fields.Many2one("account.journal", domain="[('type', '=', 'sale')]")
    account_id = fields.Many2one("account.account", "Account")
    category_id = fields.Many2one("product.category", "Category", required=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    credit_limit = fields.Float("Credit limit", default=lambda self: float(self.env["ir.config_parameter"].get_param('wallet.wallet_credit_limit')))
    product_external_relation_id = fields.Char(related="product_id.categ_id.external_relation_id")
    parent_wallet_id = fields.Many2one('wallet.category', compute='_compute_parent_wallet', compute_sudo=True, store=True)
    child_wallet_ids = fields.One2many('wallet.category', 'parent_wallet_id', store=True)
    parent_wallet_count = fields.Integer(compute='_compute_parent_wallet', compute_sudo=True)

    @api.depends('category_id', 'company_id')
    def _compute_parent_wallet(self):
        for wallet_categ_id in self:
            wallet_categ_id = wallet_categ_id.with_context({
                'company_id': wallet_categ_id.company_id.id,
                'company_ids': wallet_categ_id.company_id.ids,
                'allowed_company_ids': wallet_categ_id.company_id.ids,
                })
            wallet_categ_id.parent_wallet_id = wallet_categ_id.get_wallet_by_category_id(wallet_categ_id.category_id.parent_id) if not wallet_categ_id.is_default_wallet else False
            wallet_categ_id.parent_wallet_count = wallet_categ_id._get_parent_count()

    def _get_parent_count(self):
        self.ensure_one()
        return 1 + self.parent_wallet_id._get_parent_count() if self.parent_wallet_id else 0

    @api.depends('default_wallet_category_id')
    def _compute_is_default_wallet(self):
        for wallet in self:
            wallet.is_default_wallet = wallet.id == wallet.default_wallet_category_id.id

    @api.model
    def default_get(self, vals):
        # company_id is added
        rslt = super().default_get(vals + ['company_id'])
        return rslt

    # Used for API compatibility
    def _parse_get_wallet_amount_params(self, partner_id, wallet_category_id):
        if type(partner_id) == int:
            partner_id = self.env["res.partner"].browse(partner_id)
        if type(wallet_category_id) == int:
            wallet_category_id = self.env["wallet.category"].browse([wallet_category_id])
        elif not wallet_category_id:
            wallet_category_id = self
        return partner_id, wallet_category_id

    def get_wallet_amount(self, partner_id, wallet_category_id=False):
        partner_id, wallet_category_id = self._parse_get_wallet_amount_params(partner_id, wallet_category_id)
        return self._get_wallet_amount(partner_id, wallet_category_id)

    def _get_wallet_amount(self, partner_id, wallet_category_id):
        if wallet_category_id:

            wallet_moves = self._get_related_partner_wallet_moves(partner_id, wallet_category_id)

            if wallet_moves:
                amount_total = sum(wallet_moves.mapped(lambda move_line: move_line.price_unit if move_line.move_id.type == 'out_invoice' else -move_line.price_unit))
                return float_round(amount_total, precision_digits=self.company_id.currency_id.decimal_places)

        return 0

    def _get_related_partner_wallet_moves(self, partner_id, wallet_category_id):
        return self.env["account.move"].search(self._get_related_partner_wallet_moves_domain(partner_id)).invoice_line_ids.filtered(lambda line_id: line_id.product_id in wallet_category_id.product_id)

    def _get_related_partner_wallet_moves_domain(self, partner_id):
        return [
            ("partner_id", "=", partner_id.id),
            ('state', '=', 'posted'),
        ]

    @api.model
    def create(self, values):
        wallet_id = super().create(values)

        if "product_id" not in values:
            product_id = self.env["product.product"].create({
                "categ_id": wallet_id.category_id.id,
                "property_account_income_id": wallet_id.account_id.id,
                "taxes_id": False,
                "type": "service",
                "list_price": 0.0,
                "supplier_taxes_id": False,
                "name": wallet_id.name,
                })

            wallet_id.product_id = product_id

        self.env['res.partner'].search([])._compute_json_dict_wallet_amounts()
        return wallet_id

    def get_wallet_by_category_id(self, category_id):
        if not category_id:
            return self.env.company.default_wallet_category_id

        wallet_id = self.env["wallet.category"].search([("category_id", "=", category_id.id)])
        if not wallet_id:
            wallet_id = self.get_wallet_by_category_id(category_id.parent_id)

        wallet_id = wallet_id[0]
        return wallet_id

    def find_next_available_wallet(self, partner_id, category_id):

        wallet_id = self.env["wallet.category"].search([("category_id", "=", category_id.id)])
        if not wallet_id:
            if category_id.parent_id:
                wallet_id = self.find_next_available_wallet(partner_id, category_id.parent_id)
            else:
                wallet_id = self.env.company.default_wallet_category_id

        if self.get_wallet_amount(partner_id, wallet_id) > -abs(wallet_id.credit_limit):
            return wallet_id
        elif category_id == self.env.company.default_wallet_category_id:
            return False
        else:
            if category_id.parent_id:
                wallet_id = self.find_next_available_wallet(partner_id, category_id.parent_id)
            else:
                wallet_id = self.env.company.default_wallet_category_id
            return wallet_id
