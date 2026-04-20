{
    'name': 'ACL Role Management',
    'version': '19.0.1',
    'summary': 'custom module',
    'author': 'Vidhya',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'stock', 'account','purchase', 'crm','sale_management', 'stock'],
    'data': [

        'security/security.xml',
        'security/ir.model.access.csv',


        'views/sale_order_views.xml', 
    ],
    'installable': True,
}