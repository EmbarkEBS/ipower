{
    'name': 'ACL Role Management',
    'version': '19.0.1',
    'depends': ['base', 'sale', 'stock', 'account','purchase' , 'crm','sale_management', 'stock'],
    'data': [
<<<<<<< HEAD
       # 'security/security.xml',
        #'security/ir.model.access.csv',
=======
        'security/security.xml',
        'security/ir.model.access.csv',
>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25

        'views/sale_order_views.xml', 
    ],
    'installable': True,
}