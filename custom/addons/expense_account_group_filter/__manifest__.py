{
    "name": "Expense Account Group Filter",
    "version": "19.0.1.1.0",
    "category": "Accounting/Expenses",
    "summary": "Account group filtering and conditional expense fields",
    "depends": [
        "hr_expense",
        "hr",
        "account",
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/expense_vehicle_views.xml",
        "views/hr_expense_views.xml",
    ],
    "installable": True,
    "application": False,
}
