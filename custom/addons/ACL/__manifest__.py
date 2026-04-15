{
    'name': 'ACL Role Management',
    'version': '1.0',
    'depends': ['base', 'sale', 'stock', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}