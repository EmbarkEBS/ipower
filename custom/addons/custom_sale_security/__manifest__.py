{
    'name': 'Custom Sale Security',
    'version': '17.0.1.0.0',
    'depends': ['sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/quotation_document_views.xml',
    ],
    'installable': True,
}