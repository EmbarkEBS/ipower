{
    "name": "Custom Delivery Slip Report",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "summary": "Custom Delivery Slip PDF Report",
    "depends": ["stock"],
    "author": "Embark",
    "license": "LGPL-3",
    "data": [
        "report/delivery_slip_report.xml",
        "report/delivery_slip_template.xml",
        'views/delivery_view.xml',        
        'views/report_external_layout.xml',
    ],
    "installable": True,
    "application": False,
}
