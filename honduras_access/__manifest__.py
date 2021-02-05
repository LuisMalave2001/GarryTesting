# -*- coding: utf-8 -*-
{
    'name': 'Honduras Access Rights',

    'summary': """ Honduras Access Rights """,

    'description': """
        Honduras Access Rights
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Extra Tools',
    'version': '1.2',


    'depends': [
        'account',
        'account_reports',
        'account_asset',
        'point_of_sale',
        'hr_payroll_extends',
        'school_base',
    ],

    'data': [
        'data/ir_module_category_data.xml',
        'data/res_groups_data.xml',
        'security/ir.model.access.csv',
        'views/account_menus.xml',
        'views/res_partner_make_sale_views.xml',
        'views/pos_session_views.xml',
        'views/hr_contract_views.xml',
        'views/account_asset_views.xml',
        'views/res_users_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/res_partner_views.xml',
    ],
}
