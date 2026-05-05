# -*- coding: utf-8 -*-
{
    'name': 'Sale Internal Cost',
    'version': '1.0',
    'depends': ['sale', 'account'],
    'author': 'vidhya',
    'category': 'Sales',
    'summary': 'Add Freight, Duty, Misc to Sale Order and include in price',
    'data': [
        'views/sale_order_views.xml',
        'views/report_saleorder.xml',
    ],
    'installable': True,
    'application': False,
}