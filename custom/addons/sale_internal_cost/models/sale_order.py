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

    @api.onchange('freight', 'duty', 'misc', 'order_line', 'apply_internal_cost')
    def _onchange_apply_extra_cost(self):
        for order in self:

            if not order.apply_internal_cost:
                continue

            lines = order.order_line.filtered(lambda l: l.product_id)
            if not lines:
                continue

            total_extra = order.total_extra or 0.0
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0

            extra_per_unit = total_extra / total_qty

            for line in lines:

                # Ensure base price exists
                if not line.base_price:
                    line.base_price = line.price_unit

                # Always calculate from base price
                line.price_unit = line.base_price + extra_per_unit


# =========================
# SALE ORDER LINE
# =========================
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    base_price = fields.Float(
        string="Base Price",
        readonly=True
    )

    @api.onchange('product_id')
    def _onchange_product_set_base(self):
        for line in self:
            if line.product_id:
                line.base_price = line.price_unit or line.product_id.lst_price

    @api.onchange('price_unit')
    def _onchange_price_update_base(self):
        for line in self:
            if line.price_unit:
                line.base_price = line.price_unit

    @api.onchange('product_uom_qty')
    def _onchange_qty_reapply_extra(self):
        for line in self:
            order = line.order_id

            if not order or not order.apply_internal_cost:
                continue

            lines = order.order_line.filtered(lambda l: l.product_id)
            if not lines:
                continue

            total_extra = order.total_extra or 0.0
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0

            extra_per_unit = total_extra / total_qty

            for l in lines:
                if not l.base_price:
                    l.base_price = l.price_unit

                l.price_unit = l.base_price + extra_per_unit