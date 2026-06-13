from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    approval_manager_id = fields.Many2one(
        "res.users",
        string="Approval Manager",
        config_parameter="sale_order_approval.approval_manager_id",
    )

    min_markup = fields.Float(
        string="Minimum Markup %",
        default=20,
        config_parameter="sale_order_approval.min_markup",
    )

    max_order_value = fields.Float(
        string="Maximum Order Value (AED)",
        default=10000,
        config_parameter="sale_order_approval.max_order_value",
    )