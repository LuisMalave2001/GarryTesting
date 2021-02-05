# -*- coding: utf-8 -*-
{
    'name': 'Payroll Extensions',

    'summary': """ Payroll Extensions """,

    'description': """
        Payroll Extensions
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Payroll',
    'version': '0.1',

    'depends': [
        'hr_payroll',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/hr_loan_security.xml',
        'security/hr_loan_payment_security.xml',
        'security/hr_savings_security.xml',
        'security/hr_savings_payment_security.xml',
        'views/hr_payroll_structure_type_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_loan_views.xml',
        'views/hr_savings_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_contribution_table_views.xml',
        'data/ir_actions_server_data.xml',
    ],
}