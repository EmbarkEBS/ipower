from odoo import fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    account_group_id = fields.Many2one(
        "account.group",
        string="Account Group",
    )