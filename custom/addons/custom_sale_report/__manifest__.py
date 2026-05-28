{
    'name': 'Custom Sale Order Report',
    'version': '17.0.1.0',
    'category': 'Sales',
    'summary': 'Custom Sales Order PDF Report',
    'depends': ['sale'],
    'author': 'Embark',
    'license': 'LGPL-3',

    'data': [
        'reports/sale_report.xml',
        'reports/sale_order_template.xml',
    ],

    'installable': True,
    'application': False,
}