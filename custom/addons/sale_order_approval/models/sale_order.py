from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
_inherit = "sale.order"

```
approval_required = fields.Boolean(
    string="Approval Required",
    copy=False,
    readonly=True,
)

approval_approved = fields.Boolean(
    string="Approved",
    copy=False,
    readonly=True,
)

approval_reason = fields.Text(
    string="Approval Reason",
    copy=False,
    readonly=True,
)

can_approve = fields.Boolean(
    compute="_compute_can_approve",
    store=False,
)

@api.depends()
def _compute_can_approve(self):
    settings = self.env["sale.approval.settings"].search([], limit=1)

    manager_id = settings.approval_manager_id.id if settings else False

    for order in self:
        order.can_approve = (
            self.env.user.id == manager_id
        )

def _get_settings(self):
    settings = self.env[
        "sale.approval.settings"
    ].search([], limit=1)

    if not settings:
        raise UserError(
            _("Please configure Approval Settings.")
        )

    return settings

def _create_approval_activity(self):

    self.ensure_one()

    settings = self._get_settings()

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
        user_id=settings.approval_manager_id.id,
        summary="Quotation Approval",
        note=self.approval_reason or "",
    )

def _evaluate_approval(self):

    settings = self._get_settings()

    for order in self:

        approval_required = False
        reasons = []

        company_currency = (
            order.company_id.currency_id
        )

        total_cost = 0.0
        total_sale = 0.0

        below_cost_products = []

        for line in order.order_line:

            if line.display_type:
                continue

            cost_total = (
                line.product_id.standard_price
                * line.product_uom_qty
            )

            sale_total = line.price_subtotal

            if order.currency_id != company_currency:

                sale_total = (
                    order.currency_id._convert(
                        sale_total,
                        company_currency,
                        order.company_id,
                        order.date_order
                        or fields.Date.today(),
                    )
                )

            total_cost += cost_total
            total_sale += sale_total

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

        # MARKUP CHECK

        if total_cost > 0:

            markup = (
                (total_sale - total_cost)
                / total_cost
            ) * 100

            if markup < settings.min_markup:
                approval_required = True
                reasons.append(
                    f"Markup {markup:.2f}% is below minimum {settings.min_markup}%"
                )

        # ORDER VALUE CHECK

        order_value = order.amount_total

        if order.currency_id != company_currency:

            order_value = (
                order.currency_id._convert(
                    order.amount_total,
                    company_currency,
                    order.company_id,
                    order.date_order
                    or fields.Date.today(),
                )
            )

        if order_value > settings.max_order_value:

            approval_required = True

            reasons.append(
                f"Order value exceeds {settings.max_order_value:.2f} AED"
            )

        # BELOW COST CHECK

        if below_cost_products:

            approval_required = True

            reasons.append(
                "Products below cost:\n%s"
                % "\n".join(below_cost_products)
            )

        previous_required = order.approval_required

        values = {
            "approval_required": approval_required,
            "approval_reason": "\n\n".join(reasons),
        }

        if approval_required:

            if not previous_required:
                values["approval_approved"] = False

        else:

            values["approval_approved"] = False

        order.update(values)

        if approval_required:
            order._create_approval_activity()

@api.model_create_multi
def create(self, vals_list):

    orders = super().create(vals_list)

    orders._evaluate_approval()

    return orders

def write(self, vals):

    res = super().write(vals)

    watched_fields = {
        "order_line",
        "currency_id",
        "pricelist_id",
        "partner_id",
    }

    if watched_fields.intersection(vals):

        self.write({
            "approval_approved": False,
        })

        self._evaluate_approval()

    return res

def action_approve_quotation(self):

    self.ensure_one()

    settings = self._get_settings()

    if self.env.user != settings.approval_manager_id:
        raise UserError(
            _("Only the configured Approval Manager can approve.")
        )

    self.update({
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

    return True

def action_confirm(self):

    for order in self:

        if (
            order.approval_required
            and not order.approval_approved
        ):
            raise UserError(
                _(
                    "Manager approval is required before confirmation."
                )
            )

    return super().action_confirm()
```
