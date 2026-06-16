from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    account_group_id = fields.Many2one(
        "account.group",
        string="Account Group"
    )

    @api.onchange("account_group_id")
    def _onchange_account_group_id(self):
        self.account_id = False

        if not self.account_group_id:
            return {}

        start = self.account_group_id.code_prefix_start
        end = self.account_group_id.code_prefix_end

        accounts = self.env["account.account"].search([
            ("code", ">=", start),
            ("code", "<=", end),
        ])

        return {
            "domain": {
                "account_id": [("id", "in", accounts.ids)]
            }
        }
