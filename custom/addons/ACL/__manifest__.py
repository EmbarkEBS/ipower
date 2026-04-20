{
    'name': 'ACL Role Management',
    'version': '19.0.1',
    'depends': ['base', 'sale', 'stock', 'account','purchase', 'crm','sale_management', 'stock'],
    'data': [
<<<<<<< HEAD

        'security/security.xml',
=======
       # 'security/security.xml',
>>>>>>> parent of 3936c5e (bug fix add po to so 1)
        'security/ir.model.access.csv',


        'views/sale_order_views.xml', 
    ],
    'installable': True,
}