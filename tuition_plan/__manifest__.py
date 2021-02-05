# -*- coding: utf-8 -*-
{
    'name': 'Tuition Plan',

    'summary': """ Tuition Plan """,

    'description': """
        Tuition Plan
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Accounting',
    'version': '1.0',

    'depends': [
        'account',
        'sale_management',
        'base_automation',
        'school_base',
        'school_finance',
        'multiple_discounts',
        'school_statement_report',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/tuition_plan_security.xml',
        'data/base_automation_data.xml',
        'data/ir_actions_server_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'views/tuition_plan_views.xml',
        'views/res_partner_views.xml',
        'views/tuition_plan_report_views.xml',
    ],
}