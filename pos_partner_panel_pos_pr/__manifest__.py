{
    'name': "Point of sale partner panel pos pr",

    'summary': """Helping panel pos pr to search quickly any customer""",

    'description': """Helping panel pos pr to search quickly any customer""",

    'author': "Eduwebgroup",

    'website': "http://www.eduwebgroup.com",

    'category': 'Sales/Point Of Sale',
    'version': '0.1',

    'depends': ['pos_partner_panel', 'pos_pr'],

    'data': [
        'views/assets.xml',
    ],

    'qweb': [
        'static/src/xml/screens.xml',
    ],

    'installable': True,
    'auto_install': True,

}