# -*- coding: utf-8 -*-
{
    'name': "School Wallet",

    'summary': """Wallet to students""",

    'description': """Wallet to students and parents, <b>Etc</b>""",

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Wallet',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'wallet',
        'school_base',
        'school_finance',
    ],

    # always loaded
    'data': [
        'views/account_move_views.xml',
        'wizard/load_wallet.xml',
        # 'wizard/pay_with_wallet.xml',
    ],

}
