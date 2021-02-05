# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase
# from odoo import models, fields, _, api, SUPERUSER_ID, modules
from odoo.modules.module import load_openerp_module

# -*- encoding: utf-8 -*-

from odoo.addons.account.tests.account_test_savepoint import AccountTestInvoicingCommon
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import Form


@tagged('post_install', '-at_install')
class TestWallet(TransactionCase):
    """ Every test will have the next initial case:
        Wallet a, b, c, d, e, f, g,

        ==WALLET==STRUCTURE==
            =============
            =      - G  =
            =   -C-|    =
            =   |  - F  =
            = A-|       =
            =   |  - E  =
            =   -B-|    =
            =      - D  =
            =============

        Every wallet has a limit of 0 and a 0
        There will be a test_partner to play with
        And a payment default builder function, invoice builder function
    """

    def setUp(self):
        super().setUp()

        # Create user.
        user = self.env['res.users'].create({'name': 'Because I am accountman!', 'login': 'accountman', 'groups_id': [(6, 0, self.env.user.groups_id.ids), (4, self.env.ref('account.group_account_user').id)], })
        user.partner_id.email = 'accountman@test.com'

        # Shadow the current environment/cursor with one having the report user.
        # This is mandatory to test access rights.
        self.env = self.env(user=user, context={'allowed_company_ids': self.env.company.ids})
        self.cr = self.env.cr

        def _create_wallet_and_category(name: str, parent: object = None) -> dict:
            category_id = self.env['product.category'].create({'parent_id': getattr(parent, 'id', False), 'name': 'Category For Wallet (%s)' % name, })

            wallet_categ_id = self.env['wallet.category'].create({
                'name': 'Wallet (%s)' % name,
                'company_id': self.env.company.id,
                'category_id': category_id.id,
                'account_id': self.wallet_account_id.id,
                'journal_category_id': self.testing_wallet_journal.id,
            })

            return {'category_id': category_id, 'wallet_categ_id': wallet_categ_id, }

        def _build_test_partner_params():
            return {'name': 'Test Partner', 'company_id': self.env.company.id}

        self.test_partner = self.env['res.partner'].create(_build_test_partner_params())

        self.wallet_account_type = self.env['account.account.type'].create({'name': 'TestingWalletAccountIdType', 'type': 'other', 'internal_group': 'liability'})

        self.wallet_account_id = self.env['account.account'].create({'code': '123321123321123321', 'name': 'Testing Wallet Account', 'user_type_id': self.wallet_account_type.id, })
        self.testing_wallet_journal = self.env['account.journal'].create({'code': 'TESTINGJRNL/WALSSS/', 'type': 'sale', 'name': 'Testing Unit Wallet', })

        # Create wallets and category
        # Wallet structure for this testing
        #      - G
        #   -C-|
        #   |  - F
        # A-|
        #   |  - E
        #   -B-|
        #      - D
        #

        self.default_wallet_category_id = self.env.company.default_wallet_category_id
        self.default_sale_journal_id = self.env['account.journal'].search([('company_id', '=', self.env.company.id), ('type', '=', 'sale')], limit=1)

        # Is used for get_wallet_balances_dict method
        self.wallet_list = self.default_wallet_category_id

        wlt_categ_a = _create_wallet_and_category('A')
        self.wallet_a = wlt_categ_a['wallet_categ_id']
        self.categ_a = wlt_categ_a['category_id']
        self.wallet_list += self.wallet_a

        wlt_categ_b = _create_wallet_and_category('B', self.categ_a)
        self.wallet_b = wlt_categ_b['wallet_categ_id']
        self.categ_b = wlt_categ_b['category_id']
        self.wallet_list += self.wallet_b

        wlt_categ_c = _create_wallet_and_category('C', self.categ_a)
        self.wallet_c = wlt_categ_c['wallet_categ_id']
        self.categ_c = wlt_categ_c['category_id']
        self.wallet_list += self.wallet_c

        wlt_categ_d = _create_wallet_and_category('D', self.categ_b)
        self.wallet_d = wlt_categ_d['wallet_categ_id']
        self.categ_d = wlt_categ_d['category_id']
        self.wallet_list += self.wallet_d

        wlt_categ_e = _create_wallet_and_category('E', self.categ_b)
        self.wallet_e = wlt_categ_e['wallet_categ_id']
        self.categ_e = wlt_categ_e['category_id']
        self.wallet_list += self.wallet_e

        wlt_categ_f = _create_wallet_and_category('F', self.categ_c)
        self.wallet_f = wlt_categ_f['wallet_categ_id']
        self.categ_f = wlt_categ_f['category_id']
        self.wallet_list += self.wallet_f

        wlt_categ_g = _create_wallet_and_category('G', self.categ_c)
        self.wallet_g = wlt_categ_g['wallet_categ_id']
        self.categ_g = wlt_categ_g['category_id']
        self.wallet_list += self.wallet_g

    def _build_payment_params(self, payment_amount: float = 0.0, wallet_categ_id: int = False):
        default_payment_method_id = self.env['account.payment.method'].search([('payment_type', '=', 'inbound')], limit=1).id
        default_journal_id = self.env['account.journal'].search([('company_id', '=', self.env.company.id), ('type', 'in', ('bank', 'cash'))], limit=1).id
        return {
            'amount': payment_amount,
            'payment_method_id': default_payment_method_id,
            'journal_id': default_journal_id,
            'partner_id': self.test_partner.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'wallet_id': wallet_categ_id,
        }

    def _create_payment(self, payment_amount: float = 0.0, wallet_categ_id: int = False):
        payment_id = self.env['account.payment'].create(self._build_payment_params(payment_amount, wallet_categ_id))
        payment_id.post()
        return payment_id

    def _get_partner_wallet_balances_dict(self):
        return self.test_partner.get_wallet_balances_dict(self.wallet_list.ids)

    def _build_product_by_wallet(self, wallet_categ):
        return self.env['product.product'].create({
            'name': 'Product - wallet %s' % wallet_categ.name,
            'categ_id': wallet_categ.category_id.id
        })

    def _build_test_invoice(self, product_list: list):
        invoice = self.env['account.move'].create({
            'partner_id': self.test_partner.id,
            'journal_id': self.default_sale_journal_id.id,
            'type': 'out_invoice',
        })
        invoice.write({'invoice_line_ids': [(0, 0, {
            'product_id': self._build_product_by_wallet(product_vals['categ_id']),
            'price_unit': product_vals['amount'],
            'quantity': 1,
            'account_id': self.default_sale_journal_id.default_debit_account_id})
            for product_vals in product_list],
        })
        return invoice

    #############################
    # --------- Tests --------- #
    #############################
    def test_should_load_100_in_default(self):
        payment_100 = self._create_payment(payment_amount=100)
        self.test_partner.load_wallet_with_payments(payment_100.ids, self.default_wallet_category_id.id, 100)

        wallet_balances = self._get_partner_wallet_balances_dict()
        self.assertEquals(wallet_balances[self.default_wallet_category_id.id], 100)

    def test_should_pay_50_and_have_50_in_default(self):
        # We pay 100 to wallet_default
        payment_100 = self._create_payment(payment_amount=100)
        self.test_partner.load_wallet_with_payments(payment_100.ids, self.default_wallet_category_id.id, 100)

        # We create an invoice with 50
        invoice = self._build_test_invoice([
            {'amount': 50, 'categ_id': self.default_wallet_category_id}
        ])
        invoice.post()

        # And we pay it with default wallet
        invoice.pay_with_wallet({
            self.default_wallet_category_id.id: 50
        })

        # And we check if everything is ok
        wallet_balances = self._get_partner_wallet_balances_dict()
        self.assertEquals(wallet_balances[self.default_wallet_category_id.id], 50)

    def test_should_load_30_in_a(self):
        # We make a payment and load the wallet with that
        payment_30 = self._create_payment(payment_amount=30)
        self.test_partner.load_wallet_with_payments(payment_30.ids, self.wallet_a.id, 30)

        # We check the values
        wallet_balances = self._get_partner_wallet_balances_dict()
        self.assertEquals(wallet_balances[self.wallet_a.id], 30)

    def test_should_have_0_in_wallet_and_25_in_default(self):
        # Default wallet: 50
        # Wallet A: 30
        # Amount to pay: 30 in A

        # Load the wallets
        payment_50 = self._create_payment(payment_amount=50)
        self.test_partner.load_wallet_with_payments(payment_50.ids, self.default_wallet_category_id.id, 50)

        payment_30 = self._create_payment(payment_amount=30)
        self.test_partner.load_wallet_with_payments(payment_30.ids, self.wallet_a.id, 30)

        # Test invoice creation
        invoice = self._build_test_invoice([
            {'amount': 55, 'categ_id': self.wallet_a},
        ])
        invoice.post()

        # Now we pay 55 in A
        invoice.pay_with_wallet({
            self.wallet_a.id: 55
        })

        # This will use 30 of A and 25 in Default
        wallet_balances = self._get_partner_wallet_balances_dict()
        self.assertEquals(wallet_balances[self.wallet_a.id], 0)
        self.assertEquals(wallet_balances[self.default_wallet_category_id.id], 25)

    def test_should_f_be_on_limit_and_c_with_5_and_invoice_15(self):
        """ Here we test the parent without default wallet
            The idea is load 20 in f, 20 in c and try to pay 40 in f having a limit of -10
            We also try to pay 5 in c to test multiple loads at once"""

        # Setting the limits
        self.wallet_f.credit_limit = -10

        # Loading the wallets
        payment_20_f = self._create_payment(payment_amount=20)
        self.test_partner.load_wallet_with_payments(payment_20_f.ids, self.wallet_f.id, 20)

        payment_20_c = self._create_payment(payment_amount=20)
        self.test_partner.load_wallet_with_payments(payment_20_c.ids, self.wallet_c.id, 20)

        # We make a invoice with a total of 40
        invoice = self._build_test_invoice([
            {'amount': 40, 'categ_id': self.wallet_f},
            {'amount': 15, 'categ_id': self.wallet_c},
        ])
        invoice.post()

        # We try to pay
        invoice.pay_with_wallet({
            self.wallet_f.id: 40,
            self.wallet_c.id: 5,
        })

        # There should be
        # -10 in F
        # 5 in C
        # And a amount residual of 10
        wallet_balances = self._get_partner_wallet_balances_dict()
        self.assertEquals(wallet_balances[self.wallet_f.id], -10)
        self.assertEquals(wallet_balances[self.wallet_c.id], 5)
        self.assertEquals(invoice.amount_residual, 10)

