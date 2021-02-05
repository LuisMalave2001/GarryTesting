# -*- coding: utf-8 -*-
{
    'name': "wallet",

    'summary': """A simple wallet that can be loaded and pay invoices""",

    'description': """The best wallet that you will see""",

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Wallet',
    'version': '1.0.3-beta',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        "account",
        "account_accountant",
        "product"
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/account_security.xml',

        'wizard/load_wallet.xml',
        'wizard/pay_with_wallet.xml',

        # Inherit views
        'views/inherited/account_payment_views.xml',
        'views/inherited/account_move.xml',
        'views/inherited/account_move_line_views.xml',
        'views/partner_views.xml',
        'views/wallet_views.xml',
        'views/config_views.xml',
        'views/templates.xml',


        'data/add_assets.xml',
        'data/category_all_wallet.xml',
        'data/menu.xml',
    ],

    'post_init_hook': 'default_settings_values',
}
