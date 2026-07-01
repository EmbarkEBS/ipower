{
    'name': 'Sale Order Create Date Editor',
    'version': '19.0.1.0.0',
    'depends': ['sale'],
     'author': 'Embark',
    'license': 'LGPL-3',
'data': [
        'views/sale_order_views.xml',
    ],
    'assets': {
    'web.assets_backend': [
        'change_create_date_module/static/src/css/sale_order.css',
    ],
},
    'installable': True,
}
