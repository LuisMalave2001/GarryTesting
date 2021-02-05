# -*- coding: utf-8 -*-
{
    'name': 'Payroll Reports',

    'summary': """ Payroll Reports """,

    'description': """
        Payroll Reports
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Payroll',
    'version': '1.0',

    'depends': [
        'hr_payroll',
        'report_xlsx',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/hr_payroll_reports_menus.xml',
        'views/hr_payslip_report_summary_xlsx_template_views.xml',
        'reports/hr_payslip_reports.xml',
        'wizards/hr_payslip_report_summary_xlsx_wizard_views.xml',
    ],
}