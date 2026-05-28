{
    "name": "Sale Dual Sequence",
    "version": "19.0.1.0.0",
    "summary": "Separate Quotation and Sale Order Sequences",
    "depends": ["sale_management", "stock", "account"],
    "data": [
        "data/sale_sequence.xml",
        "views/sale_order_views.xml",
        "reports/sale_report.xml",
    ],
    "installable": True,
    "application": True,
}