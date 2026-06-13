from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_required = fields.Boolean(
        string="Approval Required",
        copy=False,
        default=False,
    )

    approval_approved = fields.Boolean(
        string="Approved",
        copy=False,
        default=False,
    )

    approval_reason = fields.Text(
        string="Approval Reason",
        copy=False,
    )

    can_approve = fields.Boolean(
        compute="_compute_can_approve",
    )

    def _compute_can_approve(self):
        for order in self:
            order.can_approve = True

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)

        # TEMPORARY TEST
        orders.write({
            "approval_required": True,
        })

        return orders

    def action_approve_quotation(self):
        self.ensure_one()

        self.write({
            "approval_approved": True,
        })

        return True

    def action_confirm(self):
        for order in self:
            if order.approval_required and not order.approval_approved:
                raise UserError(
                    "Manager approval is required before confirmation."
                )

        return super().action_confirm()
