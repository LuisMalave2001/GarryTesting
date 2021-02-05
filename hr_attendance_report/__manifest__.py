# -*- coding: utf-8 -*-
{
    'name': 'Attendance Report',

    'summary': """ Attendance Report """,

    'description': """
        Attendance Report
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Human Resources',
    'version': '1.0',

    'depends': [
        'hr_attendance',
    ],

    'data': [
        'views/res_config_settings_views.xml',
        'reports/hr_employee_reports.xml',
        'reports/hr_employee_report_templates.xml',
        'wizards/hr_employee_report_attendance_wizard_views.xml',
    ],
}