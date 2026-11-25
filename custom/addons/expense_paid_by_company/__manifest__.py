{
    "name": "Expense Paid By Company",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Expenses",
    "summary": "Default and restrict expense payment mode to Company",
    "description": """
Expense Paid By Company
=======================

This module customizes Odoo Expenses so that:

* Employee expense configuration defaults to Company.
* New expenses are automatically Paid By Company.
* Users cannot select Paid By Employee.
* The standard expense company is not changed.
* Multi-company expense functionality remains intact.
* Existing Odoo expense accounting logic is preserved.
    """,
    "author": "Embark Interactive Private Limited",
    "website": "https://www.odoo.com",
    "license": "LGPL-3",
    "depends": [
        "hr_expense",
    ],
    "data": [
        "views/hr_employee_views.xml",
        "views/hr_expense_views.xml",
    ],
    "installable": True,
    "application": False,
}