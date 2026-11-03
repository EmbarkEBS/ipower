{
    "name": "Bill of Entry",
    "version": "19.0.2.0.0",
    "category": "Inventory/Purchase",
    "summary": "Track Bill of Entry, Purchase Orders and import invoice lines",
    "license": "LGPL-3",
    "depends": [
        "base",
        "purchase",
        "purchase_stock",
        "stock",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/bill_of_entry_views.xml",
        "views/stock_picking_views.xml",
    ],
    "application": True,
    "installable": True,
}