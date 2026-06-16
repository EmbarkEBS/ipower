from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    account_group_id = fields.Many2one(
        "account.group",
        string="Account Group"
    )

    allowed_account_ids = fields.Many2many(
        "account.account",
        compute="_compute_allowed_account_ids",
        string="Allowed Accounts",
    )

    @api.depends("account_group_id")
    def _compute_allowed_account_ids(self):
        Account = self.env["account.account"]

        for rec in self:
            rec.allowed_account_ids = False

            if not rec.account_group_id:
                continue

            start = rec.account_group_id.code_prefix_start or ""
            end = rec.account_group_id.code_prefix_end or ""

            accounts = Account.search([
                ("deprecated", "=", False),
                ("code", ">=", start),
                ("code", "<=", end),
            ])

            rec.allowed_account_ids = accounts

            if rec.account_id and rec.account_id not in accounts:
                rec.account_id = False
