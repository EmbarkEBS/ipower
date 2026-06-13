from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_required = fields.Boolean(
        copy=False
    )

    approval_approved = fields.Boolean(
        copy=False
    )

    approval_reason = fields.Text(
        copy=False
    )

    def _get_settings(self):
        icp = self.env["ir.config_parameter"].sudo()

        manager_id = int(
            icp.get_param(
                "sale_order_approval.approval_manager_id",
                default=0,
            )
        )

        min_markup = float(
            icp.get_param(
                "sale_order_approval.min_markup",
                default=20,
            )
        )

        max_order_value = float(
            icp.get_param(
                "sale_order_approval.max_order_value",
                default=10000,
            )
        )

        return manager_id, min_markup, max_order_value

    def _evaluate_approval(self):
        """
        Called whenever quotation changes
        """

        for order in self:

            manager_id, min_markup, max_order_value = (
                order._get_settings()
            )

            approval_required = False
            reasons = []

            company_currency = (
                order.company_id.currency_id
            )

            total_cost = 0.0
            total_sale = 0.0

            below_cost_products = []

            for line in order.order_line:

                cost = (
                    line.product_id.standard_price
                    * line.product_uom_qty
                )

                sale_value = line.price_subtotal

                if order.currency_id != company_currency:

                    sale_value = order.currency_id._convert(
                        sale_value,
                        company_currency,
                        order.company_id,
                        order.date_order
                        or fields.Date.today(),
                    )

                total_cost += cost
                total_sale += sale_value

                unit_price_company = line.price_unit

                if order.currency_id != company_currency:

                    unit_price_company = (
                        order.currency_id._convert(
                            line.price_unit,
                            company_currency,
                            order.company_id,
                            order.date_order
                            or fields.Date.today(),
                        )
                    )

                if (
                    unit_price_company
                    < line.product_id.standard_price
                ):
                    below_cost_products.append(
                        line.product_id.display_name
                    )

            if total_cost:

                markup = (
                    (total_sale - total_cost)
                    / total_cost
                ) * 100

                if markup < min_markup:
                    approval_required = True
                    reasons.append(
                        f"Markup {markup:.2f}% below {min_markup}%"
                    )

            order_value = order.amount_total

            if order.currency_id != company_currency:
                order_value = order.currency_id._convert(
                    order.amount_total,
                    company_currency,
                    order.company_id,
                    order.date_order
                    or fields.Date.today(),
                )

            if order_value > max_order_value:
                approval_required = True
                reasons.append(
                    f"Order value exceeds {max_order_value}"
                )

            if below_cost_products:
                approval_required = True
                reasons.append(
                    "Products below cost price:\n%s"
                    % "\n".join(below_cost_products)
                )

            old_required = order.approval_required

            order.write({
                "approval_required": approval_required,
                "approval_reason": "\n".join(reasons),
            })

            if approval_required:

                if not old_required:
                    order.approval_approved = False

                order._create_approval_activity(
                    manager_id
                )

            else:
                order.approval_approved = False

    def _create_approval_activity(self, manager_id):

        if not manager_id:
            return

        existing = self.env[
            "mail.activity"
        ].search([
            ("res_model", "=", "sale.order"),
            ("res_id", "=", self.id),
            ("summary", "=", "Quotation Approval"),
        ], limit=1)

        if existing:
            return

        self.activity_schedule(
            "mail.mail_activity_data_todo",
            user_id=manager_id,
            summary="Quotation Approval",
            note=self.approval_reason or "",
        )

    def write(self, vals):

        res = super().write(vals)

        watched_fields = {
            "order_line",
            "currency_id",
            "pricelist_id",
        }

        if watched_fields.intersection(vals):
            self._evaluate_approval()

        return res

    @api.model_create_multi
    def create(self, vals_list):

        orders = super().create(vals_list)

        orders._evaluate_approval()

        return orders

    def action_approve_quotation(self):

        self.ensure_one()

        manager_id, _, _ = self._get_settings()

        if self.env.user.id != manager_id:
            raise UserError(
                _("Only approval manager can approve.")
            )

        self.write({
            "approval_approved": True,
        })

        activities = self.env[
            "mail.activity"
        ].search([
            ("res_model", "=", "sale.order"),
            ("res_id", "=", self.id),
            ("summary", "=", "Quotation Approval"),
        ])

        activities.action_feedback(
            feedback="Approved"
        )

    def action_confirm(self):

        for order in self:

            if (
                order.approval_required
                and not order.approval_approved
            ):
                raise UserError(
                    _(
                        "Manager approval required before confirmation."
                    )
                )

        return super().action_confirm()