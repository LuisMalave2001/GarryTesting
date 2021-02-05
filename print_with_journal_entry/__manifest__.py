# -*- coding: utf-8 -*-
{
    'name': 'Print with Journal Entry',

    'summary': """ Print with Journal Entry """,

    'description': """
        Print with Journal Entry
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Invoicing',
    'version': '1.0',

    'depends': [
        'school_finance',
    ],

    'data': [
        'reports/account_move_report_templates.xml',
        'reports/account_move_reports.xml',
        'reports/account_payment_report_templates.xml',
        'reports/account_payment_reports.xml',
    ],
}