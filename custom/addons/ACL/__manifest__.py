{
    'name': 'ACL Role Management',
    'version': '19.0.1',
    'depends': ['base', 'sale', 'stock', 'account','purchase' , 'crm','sale_management','mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/sale_order_views.xml', 
    ],
    'installable': True,
    'application': True,
}