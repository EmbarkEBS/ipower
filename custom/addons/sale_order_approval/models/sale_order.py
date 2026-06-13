from odoo import fields, models
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
        string="Can Approve",
        compute="_compute_can_approve",
    )

    def _compute_can_approve(self):
        for order in self:
            order.can_approve = True

    def action_approve_quotation(self):
        self.ensure_one()
        self.approval_approved = True
        return True

    def action_confirm(self):
        for order in self:
            if order.approval_required and not order.approval_approved:
                raise UserError(
                    "Manager approval is required before confirmation."
                )

        return super().action_confirm()
