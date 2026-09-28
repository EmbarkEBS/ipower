{
    "name": "Invoice Margin Analysis",
    "version": "19.0.1.0.0",
    "category": "Accounting/Reporting",
    "summary": "Invoice-wise and product-wise margin analysis",
    "author": "Embark Interactive Private Limited",
    "license": "LGPL-3",

    "depends": [
        "account",
        "sale",
        "sale_stock",
        "stock_account",
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/invoice_margin_report_views.xml",
    ],

    "installable": True,
    "application": False,
}
