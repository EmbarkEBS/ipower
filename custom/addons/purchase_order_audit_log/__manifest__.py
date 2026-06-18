{
    "name": "Purchase Order Audit Log",
    "version": "19.0.1.0.0",
    "category": "Purchases",
    "summary": "Track PO line quantity, price and discount changes",
    "depends": ["purchase", "mail"],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "application": False,
}