# from odoo import api, fields, models
# from odoo.exceptions import UserError


# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     approval_required = fields.Boolean(copy=False, default=False)
#     approval_approved = fields.Boolean(copy=False, default=False)
#     approval_reason = fields.Text(copy=False)

#     can_approve = fields.Boolean(
#         compute="_compute_can_approve"
#     )

#     def _get_settings(self):
#         return self.env["sale.approval.settings"].search([], limit=1)

#     # --------------------------------------------------
#     # CAN APPROVE
#     # --------------------------------------------------
#     def _compute_can_approve(self):
#         settings = self._get_settings()
#         manager = settings.approval_manager_id if settings else False

#         for order in self:
#             order.can_approve = self.env.user == manager

#     # --------------------------------------------------
#     # APPROVAL ENGINE
#     # --------------------------------------------------
#     def _evaluate_approval(self):
#         settings = self._get_settings()

#         if not settings:
#             return

#         for order in self:

#             company_currency = order.company_id.currency_id

#             approval_required = False
#             reasons = []

#             total_cost_aed = 0.0
#             total_sales_aed = 0.0

#             below_cost_products = []

#             # -----------------------------------
#             # CALCULATE TOTALS
#             # -----------------------------------
#             for line in order.order_line:

#                 if line.display_type:
#                     continue

#                 # Cost in AED
#                 cost_total_aed = (
#                         line.product_id.standard_price
#                         * line.product_uom_qty
#                 )

#                 total_cost_aed += cost_total_aed

#                 # Sales value from unit price × qty
#                 sales_total_aed = line.price_subtotal

#                 if order.currency_id != company_currency:
#                     sales_total_aed = order.currency_id._convert(
#                         sales_total_aed,
#                         company_currency,
#                         order.company_id,
#                         order.date_order
#                         or fields.Date.context_today(order),
#                     )

#                 total_sales_aed += sales_total_aed

#                 unit_price_aed = line.price_unit

#                 if order.currency_id != company_currency:
#                     unit_price_aed = order.currency_id._convert(
#                         unit_price_aed,
#                         company_currency,
#                         order.company_id,
#                         order.date_order
#                         or fields.Date.context_today(order),
#                     )

#                 if unit_price_aed < line.product_id.standard_price:
#                     below_cost_products.append(
#                         line.product_id.display_name
#                     )

#             # -----------------------------------
#             # MARKUP CHECK
#             # -----------------------------------
#             markup = 0.0

#             if total_cost_aed > 0:
#                 markup = (
#                                  (total_sales_aed - total_cost_aed)
#                                  / total_cost_aed
#                          ) * 100

#             if markup < settings.min_markup:
#                 approval_required = True
#                 reasons.append(
#                     f"Markup {markup:.2f}% < "
#                     f"{settings.min_markup:.2f}%"
#                 )

#             if below_cost_products:
#                 approval_required = True
#                 reasons.append(
#                     "Below Cost Products:\n%s"
#                     % "\n".join(below_cost_products)
#                 )

#             # -----------------------------------
#             # ORDER VALUE CHECK
#             # -----------------------------------
#             order_value_aed = order.amount_total

#             if order.currency_id != company_currency:
#                 order_value_aed = order.currency_id._convert(
#                     order.amount_total,
#                     company_currency,
#                     order.company_id,
#                     order.date_order
#                     or fields.Date.context_today(order),
#                 )

#             if order_value_aed > settings.max_order_value:
#                 approval_required = True
#                 reasons.append(
#                     f"Order Value {order_value_aed:.2f} AED > "
#                     f"{settings.max_order_value:.2f} AED"
#                 )

#             # -----------------------------------
#             # UPDATE VALUES
#             # -----------------------------------
#             values = {
#                 "approval_required": approval_required,
#                 "approval_reason": "\n\n".join(reasons),
#             }

#             if approval_required:
#                 values["approval_approved"] = False

#             super(SaleOrder, order).write(values)

#             # -----------------------------------
#             # ACTIVITY
#             # -----------------------------------
#             if approval_required:
#                 order._create_activity()

#     def _create_activity(self):
#         self.ensure_one()

#         settings = self._get_settings()

#         if not settings or not settings.approval_manager_id:
#             return

#         existing = self.env["mail.activity"].search([
#             ("res_model", "=", "sale.order"),
#             ("res_id", "=", self.id),
#             ("summary", "=", "Quotation Approval"),
#         ], limit=1)

#         if existing:
#             existing.note = self.approval_reason or ""
#             return

#         self.activity_schedule(
#             "mail.mail_activity_data_todo",
#             user_id=settings.approval_manager_id.id,
#             summary="Quotation Approval",
#             note=self.approval_reason or "",
#         )

#     # --------------------------------------------------
#     # CREATE
#     # --------------------------------------------------
#     @api.model_create_multi
#     def create(self, vals_list):
#         orders = super().create(vals_list)
#         orders._evaluate_approval()
#         return orders

#     # --------------------------------------------------
#     # WRITE
#     # --------------------------------------------------
#     def write(self, vals):
#         res = super().write(vals)

#         watched_fields = {
#             "order_line",
#             "pricelist_id",
#             "currency_id",
#             "partner_id",
#         }

#         if watched_fields.intersection(vals):
#             self._evaluate_approval()

#         return res

#     # --------------------------------------------------
#     # APPROVE
#     # --------------------------------------------------
#     def action_approve_quotation(self):
#         self.ensure_one()

#         settings = self._get_settings()

#         if (
#                 not settings
#                 or self.env.user != settings.approval_manager_id
#         ):
#             raise UserError(
#                 "Only Approval Manager can approve."
#             )

#         self.write({
#             "approval_approved": True,
#         })

#         activities = self.env["mail.activity"].search([
#             ("res_model", "=", "sale.order"),
#             ("res_id", "=", self.id),
#             ("summary", "=", "Quotation Approval"),
#         ])

#         activities.action_feedback(
#             feedback="Approved"
#         )

#         return True

#     # --------------------------------------------------
#     # CONFIRM
#     # --------------------------------------------------
#     def action_confirm(self):
#         for order in self:

#             if (
#                     order.approval_required
#                     and not order.approval_approved
#             ):
#                 raise UserError(
#                     "Approval required before confirming quotation."
#                 )

#         return super().action_confirm()



# from odoo import api, fields, models
# from odoo.exceptions import UserError


# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     approval_required = fields.Boolean(copy=False, default=False)
#     approval_approved = fields.Boolean(copy=False, default=False)
#     approval_reason = fields.Text(copy=False)

#     can_approve = fields.Boolean(
#         compute="_compute_can_approve"
#     )

#     def _get_settings(self):
#         return self.env["sale.approval.settings"].search([], limit=1)

#     # --------------------------------------------------
#     # CAN APPROVE
#     # --------------------------------------------------
#     def _compute_can_approve(self):
#         settings = self._get_settings()
#         manager = settings.approval_manager_id if settings else False

#         for order in self:
#             order.can_approve = self.env.user == manager

#     # --------------------------------------------------
#     # APPROVAL ENGINE
#     # --------------------------------------------------
#     def _evaluate_approval(self):
#         settings = self._get_settings()

#         if not settings:
#             return

#         for order in self:

#             company_currency = order.company_id.currency_id

#             approval_required = False
#             reasons = []

#             total_cost_aed = 0.0
#             total_sales_aed = 0.0

#             below_cost_products = []

#             for line in order.order_line:

#                 if line.display_type:
#                     continue

#                 reasons.append(
#                     f"Qty={line.product_uom_qty}"
#                 )
#                 reasons.append(
#                     f"PriceUnit={line.price_unit}"
#                 )
#                 reasons.append(
#                     f"Discount={line.discount}"
#                 )
#                 reasons.append(
#                     f"Subtotal={line.price_subtotal}"
#                 )

#                 # -----------------------------------
#                 # COST (AED)
#                 # -----------------------------------
#                 cost_price_aed = line.product_id.standard_price

#                 cost_total_aed = (
#                     cost_price_aed * line.product_uom_qty
#                 )

#                 total_cost_aed += cost_total_aed

#                 # -----------------------------------
#                 # SALES TOTAL -> AED
#                 # -----------------------------------
#                 sales_total_aed = line.price_subtotal

#                 reasons.append(
#                     f"{line.product_id.display_name} | Qty={line.product_uom_qty}"
#                 )
#                 reasons.append(
#                     f"Price Unit={line.price_unit}"
#                 )
#                 reasons.append(
#                     f"Subtotal={line.price_subtotal}"
#                 )

#                 if order.currency_id != company_currency:
#                     sales_total_aed = order.currency_id._convert(
#                         sales_total_aed,
#                         company_currency,
#                         order.company_id,
#                         fields.Date.context_today(order),
#                     )

#                 total_sales_aed += sales_total_aed

#                 # -----------------------------------
#                 # UNIT PRICE -> AED
#                 # -----------------------------------
#                 unit_price_aed = line.price_unit

#                 if order.currency_id != company_currency:
#                     unit_price_aed = order.currency_id._convert(
#                         line.price_unit,
#                         company_currency,
#                         order.company_id,
#                         fields.Date.context_today(order),
#                     )

#                 # -----------------------------------
#                 # BELOW COST CHECK
#                 # -----------------------------------
#                 if unit_price_aed < cost_price_aed:
#                     below_cost_products.append(
#                         line.product_id.display_name
#                     )

#             # -----------------------------------
#             # MARKUP CHECK
#             # -----------------------------------
#             if total_cost_aed > 0:

#                 markup = (
#                     (total_sales_aed - total_cost_aed)
#                     / total_cost_aed
#                 ) * 100
#                 reasons.append(f"Cost={total_cost_aed}")
#                 reasons.append(f"Sales={total_sales_aed}")
#                 reasons.append(f"Markup={markup}")

#                 if round(markup, 2) < round(settings.min_markup, 2):
#                     approval_required = True
#                     reasons.append(
#                         f"Markup {markup:.2f}% < {settings.min_markup:.2f}%"
#                     )

#             # -----------------------------------
#             # ORDER VALUE CHECK
#             # -----------------------------------
#             order_value_aed = order.amount_total

#             if order.currency_id != company_currency:
#                 order_value_aed = order.currency_id._convert(
#                     order.amount_total,
#                     company_currency,
#                     order.company_id,
#                     fields.Date.context_today(order),
#                 )

#             if order_value_aed > settings.max_order_value:
#                 approval_required = True
#                 reasons.append(
#                     f"Order Value {order_value_aed:.2f} AED > "
#                     f"{settings.max_order_value:.2f} AED"
#                 )

#             # -----------------------------------
#             # BELOW COST CHECK
#             # -----------------------------------
#             if below_cost_products:
#                 approval_required = True
#                 reasons.append(
#                     "Below Cost Products:\n%s"
#                     % "\n".join(below_cost_products)
#                 )

#             # -----------------------------------
#             # UPDATE VALUES
#             # -----------------------------------
#             values = {
#                 "approval_required": approval_required,
#                 "approval_reason": "\n\n".join(reasons),
#             }

#             if approval_required:
#                 values["approval_approved"] = False

#             super(SaleOrder, order).write(values)

#             # -----------------------------------
#             # ACTIVITY
#             # -----------------------------------
#             if approval_required:
#                 order._create_activity()

#     # --------------------------------------------------
#     # ACTIVITY
#     # --------------------------------------------------
#     def _create_activity(self):
#         self.ensure_one()

#         settings = self._get_settings()

#         if not settings:
#             return

#         if not settings.approval_manager_id:
#             return

#         existing = self.env["mail.activity"].search(
#             [
#                 ("res_model", "=", "sale.order"),
#                 ("res_id", "=", self.id),
#                 ("summary", "=", "Quotation Approval"),
#             ],
#             limit=1,
#         )

#         if existing:
#             return

#         self.activity_schedule(
#             "mail.mail_activity_data_todo",
#             user_id=settings.approval_manager_id.id,
#             summary="Quotation Approval",
#             note=self.approval_reason or "",
#         )

#     # --------------------------------------------------
#     # CREATE
#     # --------------------------------------------------
#     @api.model_create_multi
#     def create(self, vals_list):
#         orders = super().create(vals_list)
#         orders._evaluate_approval()
#         return orders

#     # --------------------------------------------------
#     # WRITE
#     # --------------------------------------------------
#     def write(self, vals):
#         res = super().write(vals)

#         watched_fields = {
#             "order_line",
#             "pricelist_id",
#             "currency_id",
#             "partner_id",
#         }

#         if watched_fields.intersection(vals):
#             self._evaluate_approval()

#         return res

#     # --------------------------------------------------
#     # APPROVE
#     # --------------------------------------------------
#     def action_approve_quotation(self):
#         self.ensure_one()

#         settings = self._get_settings()

#         if (
#             not settings
#             or self.env.user != settings.approval_manager_id
#         ):
#             raise UserError(
#                 "Only Approval Manager can approve."
#             )

#         self.write({
#             "approval_approved": True,
#         })

#         activities = self.env["mail.activity"].search([
#             ("res_model", "=", "sale.order"),
#             ("res_id", "=", self.id),
#             ("summary", "=", "Quotation Approval"),
#         ])

#         activities.action_feedback(
#             feedback="Approved"
#         )

#         return True

#     # --------------------------------------------------
#     # CONFIRM
#     # --------------------------------------------------
#     def action_confirm(self):

#         for order in self:

#             if (
#                 order.approval_required
#                 and not order.approval_approved
#             ):
#                 raise UserError(
#                     "Approval required before confirming quotation."
#                 )

#         return super().action_confirm()


from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_required = fields.Boolean(copy=False, default=False)
    approval_approved = fields.Boolean(copy=False, default=False)
    approval_reason = fields.Text(copy=False)

    can_approve = fields.Boolean(
        compute="_compute_can_approve"
    )

    def _get_settings(self):
        return self.env["sale.approval.settings"].search([], limit=1)

    # --------------------------------------------------
    # CAN APPROVE
    # --------------------------------------------------
    def _compute_can_approve(self):
        settings = self._get_settings()
        manager = settings.approval_manager_id if settings else False

        for order in self:
            order.can_approve = self.env.user == manager

    # --------------------------------------------------
    # APPROVAL ENGINE
    # --------------------------------------------------
    def _evaluate_approval(self):
        settings = self._get_settings()

        if not settings:
            return

        for order in self:

            company_currency = order.company_id.currency_id

            approval_required = False
            reasons = []

            total_cost_aed = 0.0
            total_sales_aed = 0.0

            below_cost_products = []

            for line in order.order_line:

                if line.display_type:
                    continue

                cost_price = line.purchase_price or 0.0
                sale_price = line.price_unit or 0.0
                qty = line.product_uom_qty or 0.0
                discount = line.discount or 0.0

                reasons.append(
                    f"{line.product_id.display_name} | "
                    f"Qty={qty} Cost={cost_price} Sale={sale_price}"
                )

                # COST TOTAL
                cost_total = cost_price * qty
                total_cost_aed += cost_total

                # SALES TOTAL
                sales_total = sale_price * qty * (
                        1 - (discount / 100.0)
                )
                total_sales_aed += sales_total

                # BELOW COST CHECK
                if sale_price < cost_price:
                    below_cost_products.append(
                        f"{line.product_id.display_name} "
                        f"(Cost={cost_price:.2f}, Sale={sale_price:.2f})"
                    )
            # -----------------------------------
            # MARKUP CHECK
            # -----------------------------------
            if total_cost_aed > 0:

                markup = (
                                 (total_sales_aed - total_cost_aed)
                                 / total_cost_aed
                         ) * 100
                # reasons.append(f"Cost={total_cost_aed}")
                # reasons.append(f"Sales={total_sales_aed}")
                # reasons.append(f"Markup={markup}")

                if round(markup, 2) < round(settings.min_markup, 2):
                    approval_required = True
                    reasons.append(
                        f"Markup {markup:.2f}% < {settings.min_markup:.2f}%"
                    )

            # -----------------------------------
            # ORDER VALUE CHECK
            # -----------------------------------
            order_value_aed = order.amount_total

            if order.currency_id != company_currency:
                order_value_aed = order.currency_id._convert(
                    order.amount_total,
                    company_currency,
                    order.company_id,
                    fields.Date.context_today(order),
                )

            if order_value_aed > settings.max_order_value:
                approval_required = True
                reasons.append(
                    f"Order Value {order_value_aed:.2f} AED > "
                    f"{settings.max_order_value:.2f} AED"
                )

            # -----------------------------------
            # BELOW COST CHECK
            # -----------------------------------
            if below_cost_products:
                approval_required = True
                reasons.append(
                    "Below Cost Products:\n%s"
                    % "\n".join(below_cost_products)
                )

            # -----------------------------------
            # UPDATE VALUES
            # -----------------------------------
            values = {
                "approval_required": approval_required,
                "approval_reason": "\n\n".join(reasons),
            }

            if approval_required:
                values["approval_approved"] = False

            super(SaleOrder, order).write(values)

            # -----------------------------------
            # ACTIVITY
            # -----------------------------------
            if approval_required:
                order._create_activity()

    # --------------------------------------------------
    # ACTIVITY
    # --------------------------------------------------
    def _create_activity(self):
        self.ensure_one()

        settings = self._get_settings()

        if not settings:
            return

        if not settings.approval_manager_id:
            return

        existing = self.env["mail.activity"].search(
            [
                ("res_model", "=", "sale.order"),
                ("res_id", "=", self.id),
                ("summary", "=", "Quotation Approval"),
            ],
            limit=1,
        )

        if existing:
            return

        self.activity_schedule(
            "mail.mail_activity_data_todo",
            user_id=settings.approval_manager_id.id,
            summary="Quotation Approval",
            note=self.approval_reason or "",
        )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._evaluate_approval()
        return orders

    # --------------------------------------------------
    # WRITE
    # --------------------------------------------------
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

    # --------------------------------------------------
    # APPROVE
    # --------------------------------------------------
    def action_approve_quotation(self):
        self.ensure_one()

        settings = self._get_settings()

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

        activities = self.env["mail.activity"].search([
            ("res_model", "=", "sale.order"),
            ("res_id", "=", self.id),
            ("summary", "=", "Quotation Approval"),
        ])

        activities.action_feedback(
            feedback="Approved"
        )

        return True

    # --------------------------------------------------
    # CONFIRM
    # --------------------------------------------------
    def action_confirm(self):

        for order in self:

            if (
                    order.approval_required
                    and not order.approval_approved
            ):
                raise UserError(
                    "Approval required before confirming quotation."
                )

        return super().action_confirm()

