{
    "name": "Custom Sales Order Report",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "summary": "Custom Sales Order PDF Report",
    "depends": ["sale"],
    'author': 'Embark',
    'license': 'LGPL-3',
    "data": [
        "report/sale_order_report.xml",
        "report/sale_order_template.xml",
        'views/sale_view.xml',
    ],
    "installable": True,
    "application": False,
}
