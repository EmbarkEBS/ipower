{
    "name": "Stock Reordering Alert",
    "version": "1.0",
    "depends": ["stock", "mail"],
    "author": "Custom",
    "category": "Inventory",
    "summary": "Send alerts when stock goes below reordering minimum",
    "data": [
        "data/cron.xml",
    ],
    "installable": True,
    "application": True,
}