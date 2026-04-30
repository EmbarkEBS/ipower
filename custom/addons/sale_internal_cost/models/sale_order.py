from odoo import models, fields, api


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

                # Only update if user hasn't manually changed price
                if not line._origin or line.price_unit == line._origin.price_unit:
                    base_price = line.product_id.lst_price
                    line.price_unit = base_price + extra_per_unit


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_apply_extra(self):
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

            # Only apply if user hasn't manually changed
            if not line._origin or line.price_unit == line._origin.price_unit:
                base_price = line.product_id.lst_price
                line.price_unit = base_price + extra_per_unit