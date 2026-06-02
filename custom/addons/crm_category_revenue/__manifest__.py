{
    "name": "CRM Category Revenue",
    "version": "19.0.1.0.0",
    "category": "CRM",
    "summary": "CRM Category Amount Tracking",
    "depends": ["crm", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/crm_lead_views.xml",
        "views/crm_category_analysis_views.xml",
    ],
    "installable": True,
    "application": False,
}
