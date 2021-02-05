# -*- coding: utf-8 -*-
{
    'name': 'School Accounting Reports',

    'summary': """ Accounting reports for schools """,

    'description': """ Accounting reports for schools """,

    'author': 'Eduwebgroup',
    'website': 'http://www.Eduwebgroup.com',

    'category': 'Accounting',
    'version': '0.1',

    'depends': [
        'account_reports',
        'account_reports_extends',
        'school_finance',
    ],

    'data': [
        'views/assets.xml',
        'views/account_student_ledger_templates.xml',
        'views/account_student_ledger_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_line_views.xml',
    ],
}
