{
    "name": "Bill of Entry",
    "version": "19.0.1.0.0",
    "category": "Inventory/Purchase",
    "summary": "Manage BOE, purchase orders and import bills",
    "license": "LGPL-3",
    "depends": [
        "base",
        "purchase",
        "stock",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/bill_of_entry_views.xml",
        "views/stock_picking_views.xml",
    ],
    "application": True,
    "installable": True,
}