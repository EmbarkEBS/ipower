{
    "name": "Expense Paid By Company",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Expenses",
    "summary": "Default expense payment mode to Company",
    "description": """
Expense Paid By Company
=======================

This module customizes Odoo Expenses so that:

* New expenses default to Paid By Company.
* The default applies to all employees.
* No employee-specific configuration is required.
* Standard expense company functionality is preserved.
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
        "views/hr_expense_views.xml",
    ],
    "installable": True,
    "application": False,
}