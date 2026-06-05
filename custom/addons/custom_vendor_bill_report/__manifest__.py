{
    "name": "Custom Vendor Bill Report",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Custom Vendor Bill PDF Report",
    "depends": ["account"],
    "author": "Embark",
    "license": "LGPL-3",
    "data": [
        "report/vendor_bill_report.xml",
        "report/vendor_bill_template.xml",
        'views/vendor_bill_view.xml',
    ],
    "installable": True,
    "application": False,
}