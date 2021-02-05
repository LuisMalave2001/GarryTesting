# -*- coding: utf-8 -*-
{
    'name': 'School Statement Report',

    'summary': """ School Statement Report """,

    'description': """
        School Statement Report
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Invoicing',
    'version': '1.0',

    'depends': [
        'school_account_reports',
    ],

    'data': [
        'reports/res_partner_templates.xml',
        'reports/res_partner_reports.xml',
    ],
}