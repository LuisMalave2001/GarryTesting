{
    'name': "Point of sale partner",

    'summary': """Helping panel school to search quickly any customer""",

    'description': """Helping panel school to search quickly any customer""",

    'author': "Eduwebgroup",

    'website': "http://www.eduwebgroup.com",

    'category': 'Sales/Point Of Sale',
    'version': '0.1',

    'depends': ['point_of_sale', 'eduweb_js_utils'],

    'data': [
        'views/assets.xml',
    ],

    'qweb': [
        'static/src/xml/screens.xml',
    ],

    'installable': True,
    'auto_install': True,

}