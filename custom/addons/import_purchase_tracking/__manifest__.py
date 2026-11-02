{
    "name": "Import Purchase Tracking",
    "version": "19.0.1.0.0",
    "category": "Purchase",
    "summary": "Track BOEs, multiple purchase orders, suppliers and import charge allocations",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["purchase", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/import_boe_views.xml",
        "views/account_move_views.xml",
        "views/import_charge_allocation_views.xml",
        "views/import_purchase_menu.xml",
    ],
    "installable": True,
    "application": True,
}
