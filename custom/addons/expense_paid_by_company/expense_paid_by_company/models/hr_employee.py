from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    expense_paid_by_company = fields.Boolean(
        string="Expense Paid By Company",
        default=True,
        help=(
            "If enabled, expenses created for this employee are "
            "automatically paid by the company."
        ),
    )
