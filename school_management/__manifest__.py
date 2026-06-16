{
    'name': "school_management",

    'summary': "School Management",

    'description': """
School Management Module
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'account',
        'sale',
        'sale_management',
        'stock',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/ir_cron_data.xml',

        'views/student_view.xml',
        'views/teacher_view.xml',
        'views/subject_view.xml',
        'views/res_partner_view.xml',
        'views/menu.xml',
        'views/sale_order_view.xml',
        'views/advance_payment_wizard.xml',
        'views/account_move_view.xml',

        'wizard/sale_delivery_report_wizard.xml',
        'report/sale_delivery_report.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],

    'license': 'LGPL-3',

    'installable': True,
    'application': True,
}