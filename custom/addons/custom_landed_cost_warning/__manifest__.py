{
    'name': 'Landed Cost Warning',
    'version': '19.0.1.0.0',
    'summary': 'Prevent duplicate landed cost',
    'category': 'Inventory',

    'depends': [
        'stock_landed_costs',
        'purchase',
        'account',
    ],

    'data': [
        'views/stock_landed_cost_views.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}