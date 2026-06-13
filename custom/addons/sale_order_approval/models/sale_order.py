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
        compute="_compute_can_approve",
    )

    def _compute_can_approve(self):
        settings = self.env["sale.approval.settings"].search([], limit=1)

        manager = settings.approval_manager_id if settings else False

        for order in self:
            order.can_approve = (
                self.env.user == manager
            )

    def action_approve_quotation(self):
        self.ensure_one()

        settings = self.env[
            "sale.approval.settings"
        ].search([], limit=1)

        if (
            not settings
            or self.env.user != settings.approval_manager_id
        ):
            raise UserError(
                "Only Approval Manager can approve."
            )

        self.write({
            "approval_approved": True,
        })

        return True

    def action_confirm(self):

        for order in self:

            if (
                order.approval_required
                and not order.approval_approved
            ):
                raise UserError(
                    "Manager approval is required before confirmation."
                )

        return super().action_confirm()
