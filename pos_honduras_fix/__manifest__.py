# -*- coding: utf-8 -*-
{
    'name': "pos_honduras_fix",

    'summary': """ This is a fix for point of sale for Honduras """,

    'description': """ Fix for honduras invoices in point of sale """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of sale',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'honduras_invoices', 'point_of_sale'],

    # always loaded
    'data': [
        'views/fix_report.xml',
    ],
}
