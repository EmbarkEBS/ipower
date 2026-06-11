{
    "name": "Partner Currency Statement",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Customer/Vendor Currency Statement",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": [
        "account",
        "contacts",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/partner_views.xml",
        "views/wizard_views.xml",
        "reports/report_action.xml",
        "reports/partner_currency_statement_templates.xml",
    ],
    "installable": True,
    "application": False,
}
