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

# from odoo import api, fields, models
# from odoo.exceptions import ValidationError


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

#     vehicle_number = fields.Char(
#         string="Vehicle Number"
#     )

#     show_vehicle_number = fields.Boolean(
#         compute="_compute_show_vehicle_number",
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

#     @api.depends("account_group_id")
#     def _compute_show_vehicle_number(self):
#         for rec in self:
#             rec.show_vehicle_number = bool(
#                 rec.account_group_id
#                 and rec.account_group_id.name
#                 and "vehicle" in rec.account_group_id.name.lower()
#             )

#     @api.onchange("account_group_id")
#     def _onchange_account_group_id(self):
#         if (
#             self.account_group_id
#             and self.account_group_id.name
#             and "vehicle" not in self.account_group_id.name.lower()
#         ):
#             self.vehicle_number = False

#     @api.constrains("account_group_id", "vehicle_number")
#     def _check_vehicle_number(self):
#         for rec in self:
#             if (
#                 rec.account_group_id
#                 and rec.account_group_id.name
#                 and "vehicle" in rec.account_group_id.name.lower()
#                 and not rec.vehicle_number
#             ):
#                 raise ValidationError(
#                     "Vehicle Number is required for Vehicle related expenses."
#                 )

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

#     vehicle_number = fields.Char(
#         string="Vehicle Number"
#     )

#     employee_name = fields.Char(
#         string="Employee"
#     )

#     # employee_id = fields.Many2one(
#     #     "hr.employee",
#     #     string="Employee",
#     #     ondelete="set null"
#     # )

#     # project_name = fields.Char(
#     #     string="Project Name"
#     # )

#     sale_order_id = fields.Many2one(
#           "sale.order",
#           string="Sale Order",
#           domain="[('state', 'in', ['sale', 'done'])]",
#     )

#     show_vehicle_number = fields.Boolean(
#         compute="_compute_group_fields"
#     )

#     show_employee = fields.Boolean(
#         compute="_compute_group_fields"
#     )

#     show_project = fields.Boolean(
#         compute="_compute_group_fields"
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

#     @api.depends("account_group_id")
#     def _compute_group_fields(self):
#         for rec in self:
#             group_name = (
#                 rec.account_group_id.name.lower()
#                 if rec.account_group_id and rec.account_group_id.name
#                 else ""
#             )

#             rec.show_vehicle_number = "vehicle" in group_name

#             rec.show_employee = (
#                 group_name == "employee & hr expenses".lower()
#             )

#             rec.show_project = (
#                 group_name == "Sales & Business Development Expenses".lower()
#             )

#     @api.onchange("account_group_id")
#     def _onchange_account_group_id(self):
#         group_name = (
#             self.account_group_id.name.lower()
#             if self.account_group_id and self.account_group_id.name
#             else ""
#         )

#         if "vehicle" not in group_name:
#             self.vehicle_number = False

#         if group_name != "employee & hr expenses".lower():
#             self.employee_name = False

#         # if group_name != "employee & hr expenses".lower():
#         #       self.employee_id = False


        # if group_name != "project / service order expenses".lower():
        # if group_name != "Sales & Business Development Expenses".lower():
        #     # self.project_name = False
        #     self.sale_order_id = False


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    account_group_id = fields.Many2one(
        "account.group",
        string="Account Group",
    )

    allowed_account_ids = fields.Many2many(
        "account.account",
        compute="_compute_allowed_account_ids",
        string="Allowed Accounts",
    )

    # Vehicle Master selection
    vehicle_id = fields.Many2one(
        "expense.vehicle",
        string="Vehicle Number",
        ondelete="restrict",
    )

    # Employee selection
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
    )

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        domain="[('state', 'in', ['sale', 'done'])]",
    )

    show_vehicle_number = fields.Boolean(
        compute="_compute_group_fields",
    )

    show_employee = fields.Boolean(
        compute="_compute_group_fields",
    )

    show_project = fields.Boolean(
        compute="_compute_group_fields",
    )

    @api.depends(
        "account_group_id",
        "account_group_id.name",
    )
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

    @api.depends(
        "account_group_id",
        "account_group_id.name",
    )
    def _compute_group_fields(self):
        for rec in self:

            group_name = (
                rec.account_group_id.name.lower()
                if rec.account_group_id
                and rec.account_group_id.name
                else ""
            )

            rec.show_vehicle_number = (
                "vehicle" in group_name
            )

            rec.show_employee = (
                group_name == "employee & hr expenses"
            )

            rec.show_project = (
                group_name == "sales & business development expenses".lower()
            )

    @api.onchange("account_group_id")
    def _onchange_account_group_id(self):
        for rec in self:

            group_name = (
                rec.account_group_id.name.lower()
                if rec.account_group_id
                and rec.account_group_id.name
                else ""
            )

            if "vehicle" not in group_name:
                rec.vehicle_id = False

            if group_name != "employee & hr expenses":
                rec.employee_id = False

            if group_name != "sales & business development expenses":
                rec.sale_order_id = False

    @api.constrains(
        "account_group_id",
        "vehicle_id",
        "employee_id",
        "sale_order_id",
    )
    def _check_conditional_required_fields(self):
        for rec in self:

            group_name = (
                rec.account_group_id.name.lower()
                if rec.account_group_id
                and rec.account_group_id.name
                else ""
            )

            if "vehicle" in group_name and not rec.vehicle_id:
                raise ValidationError(
                    _("Please select a Vehicle Number.")
                )

            if (
                group_name == "employee & hr expenses"
                and not rec.employee_id
            ):
                raise ValidationError(
                    _("Please select an Employee.")
                )

            if (
                group_name == "sales & business development expenses"
                and not rec.sale_order_id
            ):
                raise ValidationError(
                    _("Please select a Sale Order.")
                )

