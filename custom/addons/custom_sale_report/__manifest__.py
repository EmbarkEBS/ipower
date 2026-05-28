{
    'name': 'Custom Sale Order Report',
    'version': '17.0.1.0',
    'category': 'Sales',
    'summary': 'Custom Sales Order PDF Report',
    'depends': ['sale'],
    'author': 'Embark',
    'license': 'LGPL-3',

    'data': [
        'report/sale_order_template.xml',
        'report/sale_report.xml',
    ],

    'installable': True,
    'application': False,
}