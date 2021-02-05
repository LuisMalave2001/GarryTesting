# -*- coding: utf-8 -*-
{
    'name': 'Honduras Checks Layout',

    'summary': """ Print HN Checks """,

    'description': """
        This module allows to print your payments on pre-printed checks.
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Invoicing',
    'version': '0.1',

    'depends': [
        'account_check_printing',
    ],

    'data': [
        'data/hn_check_printing.xml',
        'report/print_check.xml',
        'views/account_journal_views.xml',
    ],
}