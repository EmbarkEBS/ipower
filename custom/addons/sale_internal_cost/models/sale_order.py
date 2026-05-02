from odoo import models, fields, api


# =========================
# SALE ORDER
# =========================
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight = fields.Monetary(string="Freight")
    duty = fields.Monetary(string="Duty")
    misc = fields.Monetary(string="Miscellaneous")

    apply_internal_cost = fields.Boolean(
        string="Apply Internal Cost",
        default=True
    )

    total_extra = fields.Monetary(
        string="Total Extra Cost",
        compute="_compute_total_extra",
        store=True
    )

    @api.depends('freight', 'duty', 'misc')
    def _compute_total_extra(self):
        for order in self:
            order.total_extra = (
                (order.freight or 0.0)
                + (order.duty or 0.0)
                + (order.misc or 0.0)
            )

    def _recompute_prices(self):
        for order in self:

            if not order.apply_internal_cost:
                continue

            lines = order.order_line.filtered(lambda l: l.product_id)
            if not lines:
                continue

            total_extra = order.total_extra or 0.0
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0

            # Correct distribution
            extra_per_unit = round(total_extra / total_qty, 2)

            # STEP 1: Reset to base price
            for line in lines:
                if not line.base_price:
                    line.base_price = line.price_unit
                line.price_unit = line.base_price

            # STEP 2: Apply extra ONLY ONCE
            for line in lines:
                line.price_unit += extra_per_unit

    @api.onchange('freight', 'duty', 'misc', 'order_line', 'apply_internal_cost')
    def _onchange_internal_cost(self):
        self._recompute_prices()


# =========================
# SALE ORDER LINE
# =========================
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    base_price = fields.Float(string="Base Price")

    @api.onchange('product_id')
    def _onchange_product(self):
        for line in self:
            if line.product_id:
                # store initial price
                line.base_price = line.price_unit or line.product_id.lst_price

    @api.onchange('price_unit')
    def _onchange_price(self):
        for line in self:
            if line.price_unit:
                # user manually edits → update base
                line.base_price = line.price_unit

    @api.onchange('product_uom_qty')
    def _onchange_qty(self):
        for line in self:
            if line.order_id:
                line.order_id._recompute_prices()