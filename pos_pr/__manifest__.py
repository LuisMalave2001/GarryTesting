# -*- coding: utf-8 -*-
{
    'name': "POS Payment Register",

    'summary': """ Implements a payment register in POS """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Point Of Sale',
    'version': '1.1.3',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'eduweb_js_utils',
                'point_of_sale',
                'school_base',
                'school_finance'],

    'data': [
        'security/ir.model.access.csv',

        'data/products.xml',
        'data/sequence.xml',

        'views/assets.xml',
        'views/invoice_payment_views.xml',

        'views/pos_session_views.xml',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'views/account_bank_statement_cashbox_views.xml',

        'views/res_config_settings_views.xml',
    ],

    'qweb': [
        # Core
        'static/src/xml/core/chrome.xml',

        # Payment receipt
        'static/src/xml/templates/payment_reports.xml',
        'static/src/xml/templates/surcharge_reports.xml',

        'static/src/xml/screens/invoice_payment_receipt.xml',
        'static/src/xml/screens/surcharge_payment_receipt.xml',

        'static/src/xml/pos_view.xml',
        'static/src/xml/payment_register/components/invoice_list.xml',
        # 'static/src/xml/payment_register/components/dashboard.xml',

        # owl Views
        'static/src/xml/owl/screens.xml'
    ],

    'post_init_hook': 'default_settings_values',
}
