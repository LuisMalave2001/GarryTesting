{
    'name': "Point of sale partner panel school",

    'summary': """Helping panel school to search quickly any customer""",

    'description': """Helping panel school to search quickly any customer""",

    'author': "Eduwebgroup",

    'website': "http://www.eduwebgroup.com",

    'category': 'Sales/Point Of Sale',
    'version': '0.1',

    'depends': ['pos_partner_panel', 'pos_school'],

    'data': [
        'views/assets.xml',
    ],

    'qweb': [
        'static/src/xml/screens.xml',
    ],

    'installable': True,
    'auto_install': True,

}