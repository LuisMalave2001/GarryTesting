# -*- coding: utf-8 -*-
{
    'name': 'Journal Entry Printing',

    'summary': """ Journal Entry Printing """,

    'description': """
        Journal Entry Printing
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Accounting',
    'version': '1.0',

    'depends': [
        'account',
    ],

    'data': [
        'reports/account_move_templates.xml',
        'reports/account_move_reports.xml',
        'wizards/account_move_report_matrix_wizard_views.xml',
    ],
}