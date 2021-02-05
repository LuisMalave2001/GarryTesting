# -*- coding: utf-8 -*-
{
    'name': 'Send Email when Invoice is Paid',

    'summary': """ Send Email when Invoice is Paid """,

    'description': """
        Send Email when Invoice is Paid
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Invoicing',
    'version': '1.0',

    'depends': [
        'account',
    ],

    'data': [
        'data/mail_template_data.xml',
        'data/base_automation_data.xml',
    ],
}