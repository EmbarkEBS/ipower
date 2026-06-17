{
    "name": "Custom Purchase Order Report",
    "version": "19.0.1.0.0",
    "category": "Purchase",
    "summary": "Custom Purchase Order PDF Report",
    "depends": ["purchase"],
    'author': 'Embark',
    'license': 'LGPL-3',
    "data": [
        "report/purchase_order_report.xml",
        "report/purchase_order_template.xml",
        'views/purchase_view.xml',
        'views/report_external_layout.xml',
    ],
    "installable": True,
    "application": False,
}
