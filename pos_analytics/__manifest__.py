{
    'name': "Pos Analyitics",

    'summary': """ Improve analytics in point of sale """,

    'description': """ Add analytics accounts to point of sale products """,

    'author': "Eduwebgroup",

    'website': "http://www.eduwebgroup.com",

    'category': 'Hidden',
    'version': '1.0.0',

    'depends': ['point_of_sale', 'analytic', 'eduweb_analytics'],

    'data': [
        'data/assets.xml',
        'views/pos_order.xml',
        ],

    'qweb': [
        'static/src/xml/pos_templates.xml'
        ],

    'installable': True,
    'auto_install': True,

}
