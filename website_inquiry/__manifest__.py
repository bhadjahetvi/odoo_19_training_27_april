{
    'name': 'Website Inquiry Pro',
    'version': '2.0',
    'depends': ['website', 'crm'],
    'author': 'Your Name',
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/inquiry_templates.xml',
        'views/inquiry_views.xml',
        'views/inquiry_menu.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            'website_inquiry/static/src/js/inquiry.js',
        ],
    },
    'installable': True,
    'application': True,
}