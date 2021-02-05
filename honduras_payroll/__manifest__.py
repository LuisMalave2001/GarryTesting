# -*- coding: utf-8 -*-
{
    'name': 'Honduras Payroll',

    'summary': """ Honduras Payroll """,

    'description': """
        Honduras Payroll
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Payroll',
    'version': '1.0',

    'depends': [
        'hr_payroll_account_extends',
    ],

    'data': [
        'reports/hr_payslip_report_templates.xml',
    ],
}