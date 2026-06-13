from odoo import fields, models


class SaleApprovalSettings(models.Model):
    _name = "sale.approval.settings"
    _description = "Sale Approval Settings"

    name = fields.Char(
        default="Default Settings",
        required=True,
    )

    approval_manager_id = fields.Many2one(
        "res.users",
        required=True,
    )

    min_markup = fields.Float(
        default=20.0,
        required=True,
    )

    max_order_value = fields.Float(
        default=10000.0,
        required=True,
    )
