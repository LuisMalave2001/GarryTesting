# -*- coding: utf-8 -*-
{
    'name': 'Canteen',

    'summary': """ Canteen """,

    'description': """
        Canteen
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Sales',
    'version': '1.0',

    'depends': [
        'account',
        'sale_management',
        'portal',
        'school_finance',
    ],

    'data': [
        'security/ir.model.access.csv',
        'reports/sale_order_report_templates.xml',
        'reports/sale_order_reports.xml',
        'views/assets.xml',
        'views/canteen_menus.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/canteen_order_portal_templates.xml',
        'wizards/sale_order_report_canteen_wizard_views.xml',
        'data/ir_cron_data.xml',
    ],
}