# -*- coding: utf-8 -*-
{
    'name': 'Payroll Accounting Extensions',

    'summary': """ Payroll Accounting Extensions """,

    'description': """
        Payroll Accounting Extensions
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Payroll',
    'version': '0.1',

    'depends': [
        'hr_payroll_account',
        'hr_payroll_extends',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/hr_payslip_deduction_security.xml',
        'views/hr_contract_views.xml',
        'views/hr_loan_views.xml',
        'views/hr_savings_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/hr_payroll_structure_type_views.xml',
    ],
}