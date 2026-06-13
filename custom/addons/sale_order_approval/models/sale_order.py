from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_required = fields.Boolean(copy=False, default=False)
    approval_approved = fields.Boolean(copy=False, default=False)
    approval_reason = fields.Text(copy=False)

    can_approve = fields.Boolean(compute="_compute_can_approve")

    def _get_settings(self):
        return self.env["sale.approval.settings"].search([], limit=1)

    # -------------------------
    # CAN APPROVE FIELD
    # -------------------------
    def _compute_can_approve(self):
        settings = self._get_settings()
        manager = settings.approval_manager_id if settings else False

        for order in self:
            order.can_approve = (self.env.user == manager)

    # -------------------------
    # MAIN ENGINE (SAFE)
    # -------------------------
    def _evaluate_approval(self):
        settings = self._get_settings()
        if not settings:
            return

        company_currency = self.company_id.currency_id

        for order in self:

            approval_required = False
            reasons = []

            total_cost = 0.0
            total_sales = 0.0
            below_cost_products = []

            for line in order.order_line:
                if line.display_type:
                    continue

                cost = line.product_id.standard_price * line.product_uom_qty
                price = line.price_subtotal

                if order.currency_id != company_currency:
                    price = order.currency_id._convert(
                        price,
                        company_currency,
                        order.company_id,
                        fields.Date.context_today(order),
                    )

                total_cost += cost
                total_sales += price

                if line.price_unit < line.product_id.standard_price:
                    below_cost_products.append(line.product_id.display_name)

            # MARKUP
            if total_cost > 0:
                markup = ((total_sales - total_cost) / total_cost) * 100
                if markup < settings.min_markup:
                    approval_required = True
                    reasons.append(f"Markup {markup:.2f}% < {settings.min_markup}%")

            # ORDER VALUE
            order_value = order.amount_total

            if order.currency_id != company_currency:
                order_value = order.currency_id._convert(
                    order.amount_total,
                    company_currency,
                    order.company_id,
                    fields.Date.context_today(order),
                )

            if order_value > settings.max_order_value:
                approval_required = True
                reasons.append(
                    f"Order Value {order_value:.2f} > {settings.max_order_value}"
                )

            # BELOW COST
            if below_cost_products:
                approval_required = True
                reasons.append(
                    "Below Cost Products:\n" + "\n".join(below_cost_products)
                )

            # SAFE WRITE (avoid recursion loop)
            super(SaleOrder, order).write({
                "approval_required": approval_required,
                "approval_reason": "\n".join(reasons),
                "approval_approved": False if approval_required else order.approval_approved,
            })

            if approval_required:
                order._create_activity()

    # -------------------------
    # ACTIVITY
    # -------------------------
    def _create_activity(self):
        self.ensure_one()

        settings = self._get_settings()
        if not settings or not settings.approval_manager_id:
            return

        existing = self.env["mail.activity"].search([
            ("res_model", "=", "sale.order"),
            ("res_id", "=", self.id),
            ("summary", "=", "Quotation Approval"),
        ], limit=1)

        if existing:
            return

        self.activity_schedule(
            "mail.mail_activity_data_todo",
            user_id=settings.approval_manager_id.id,
            summary="Quotation Approval",
            note=self.approval_reason or "",
        )

    # -------------------------
    # CREATE
    # -------------------------
    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._evaluate_approval()
        return orders

    # -------------------------
    # WRITE (SAFE TRIGGER ONLY)
    # -------------------------
    def write(self, vals):
        res = super().write(vals)

        watched_fields = {
            "order_line",
            "pricelist_id",
            "currency_id",
            "partner_id",
        }

        if watched_fields.intersection(vals):
            self._evaluate_approval()

        return res

    # -------------------------
    # APPROVE
    # -------------------------
    def action_approve_quotation(self):
        self.ensure_one()

        settings = self._get_settings()

        if self.env.user != settings.approval_manager_id:
            raise UserError("Only Approval Manager can approve.")

        self.write({"approval_approved": True})

        activities = self.env["mail.activity"].search([
            ("res_model", "=", "sale.order"),
            ("res_id", "=", self.id),
            ("summary", "=", "Quotation Approval"),
        ])
        activities.action_feedback(feedback="Approved")

        return True

    # -------------------------
    # CONFIRM
    # -------------------------
    def action_confirm(self):
        for order in self:
            if order.approval_required and not order.approval_approved:
                raise UserError("Approval required before confirming quotation.")

        return super().action_confirm()
