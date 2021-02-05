# -*- coding: utf-8 -*-
{
    'name': 'School Config Checker',

    'summary': """ School Config Checker """,

    'description': """
        School Config Checker
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Extra Tools',
    'version': '1.0',

    'depends': [
        'school_finance',
    ],

    'data': [
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'views/product_category_views.xml',
    ],
}