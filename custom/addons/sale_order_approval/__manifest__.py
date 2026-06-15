{
    "name": "Sale Order Approval",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "depends": [
        "sale_management",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        # "views/res_config_settings_views.xml",
        "views/approval_settings_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
