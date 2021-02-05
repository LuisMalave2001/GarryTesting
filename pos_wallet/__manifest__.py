{
    'name': "Point of sale wallet",

    'summary': """ Add wallet features to Point of Sale module """,

    'description': """ Adds wallet features to Point of Sale module""",

    'author': "Eduwebgroup",

    'website': "http://www.eduwebgroup.com",

    'category': 'Sales/Point Of Sale',
    'version': '0.1.2',

    'depends': ['point_of_sale', 'eduweb_js_utils', 'wallet'],

    'data': [
        'security/ir.model.access.csv',

        'data/assets.xml',

        'views/views.xml',
        'views/inherited/pos_session_views.xml',
        'views/inherited/pos_config.xml',
    ],

    'qweb': [
        'static/src/xml/screen_templates.xml',
        'static/src/xml/notification_bar_templates.xml',

        'static/src/xml/pos/reports/load_wallet_reports.xml',
        'static/src/xml/owl/screens.xml',
    ],

    'installable': True,
    'auto_install': True,

}