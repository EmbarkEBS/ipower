# from odoo import api, fields, models


# class HrExpense(models.Model):
#     _inherit = "hr.expense"

#     account_group_id = fields.Many2one(
#         "account.group",
#         string="Account Group"
#     )

#     allowed_account_ids = fields.Many2many(
#         "account.account",
#         compute="_compute_allowed_account_ids",
#         string="Allowed Accounts",
#     )

#     @api.depends("account_group_id")
#     def _compute_allowed_account_ids(self):
#         Account = self.env["account.account"]

#         for rec in self:
#             rec.allowed_account_ids = False

#             if not rec.account_group_id:
#                 continue

#             start = rec.account_group_id.code_prefix_start or ""
#             end = rec.account_group_id.code_prefix_end or ""

#             accounts = Account.search([                
#                 ("code", ">=", start),
#                 ("code", "<=", end),
#             ])

#             rec.allowed_account_ids = accounts

#             if rec.account_id and rec.account_id not in accounts:
#                 rec.account_id = False

from odoo import api, fields, models
from odoo.exceptions import ValidationError


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

    vehicle_number = fields.Char(
        string="Vehicle Number"
    )

    show_vehicle_number = fields.Boolean(
        compute="_compute_show_vehicle_number",
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
                ("code", ">=", start),
                ("code", "<=", end),
            ])

            rec.allowed_account_ids = accounts

            if rec.account_id and rec.account_id not in accounts:
                rec.account_id = False

    @api.depends("account_group_id")
    def _compute_show_vehicle_number(self):
        for rec in self:
            rec.show_vehicle_number = bool(
                rec.account_group_id
                and rec.account_group_id.name
                and "vehicle" in rec.account_group_id.name.lower()
            )

    @api.onchange("account_group_id")
    def _onchange_account_group_id(self):
        if (
            self.account_group_id
            and self.account_group_id.name
            and "vehicle" not in self.account_group_id.name.lower()
        ):
            self.vehicle_number = False

    @api.constrains("account_group_id", "vehicle_number")
    def _check_vehicle_number(self):
        for rec in self:
            if (
                rec.account_group_id
                and rec.account_group_id.name
                and "vehicle" in rec.account_group_id.name.lower()
                and not rec.vehicle_number
            ):
                raise ValidationError(
                    "Vehicle Number is required for Vehicle related expenses."
                )
