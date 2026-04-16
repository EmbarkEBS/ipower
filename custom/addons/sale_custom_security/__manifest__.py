{
    'name': 'Sales ACL Role Management',
    'version': '19.0.0',
    'depends': ['base', 'sale', 'stock', 'crm'],
    'data': [
        'security/sale_groups.xml',
        'security/ir.model.access.csv',         
    ],
    'installable': True,
    'application': True,
}