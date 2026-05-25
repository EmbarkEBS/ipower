{
    'name': 'Custom  Report',
    'version': '1.0',
    'depends': ['purchase'],
    'depends': ['base', 'sale', 'stock', 'account','purchase' , 'crm','sale_management', 'stock'],
     'author': 'Embark',
    'data': [
        'reports/purchase_order_report.xml',
        'reports/purchase_order_template.xml',
        'reports/sale_order_report.xml',
        'reports/sale_order_template.xml',
    ],
    'installable': True,
}
