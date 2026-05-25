{
    'name': 'Purchase Custom Sequence',
    'version': '19.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Separate RFQ and PO Sequence',
    'depends': ['purchase'],
    'data': [
        'data/sequence.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
