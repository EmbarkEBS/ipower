from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight = fields.Monetary(string="Freight")
    duty = fields.Monetary(string="Duty")
    misc = fields.Monetary(string="Miscellaneous")

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
            lines = order.order_line.filtered(lambda l: l.product_id)

            if not lines:
                continue

            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = (order.total_extra or 0.0) / total_qty

            for line in lines:
                # ✅ ALWAYS use base_price only
                base = line.base_price or line.product_id.lst_price

                line.extra_per_unit = extra_per_unit
                line.price_unit = base + extra_per_unit

    @api.onchange('freight', 'duty', 'misc', 'order_line.product_uom_qty')
    def _onchange_extra(self):
        self._recompute_prices()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    base_price = fields.Float(string="Base Price")
    extra_per_unit = fields.Float(string="Extra / Unit")

    @api.onchange('product_id')
    def _onchange_product_set_base(self):
        for line in self:
            if line.product_id:
                # set base price once
                line.base_price = line.product_id.lst_price

                if line.order_id:
                    line.order_id._recompute_prices()

    @api.onchange('price_unit')
    def _onchange_price_unit_update_base(self):
        for line in self:
            if not line.order_id:
                continue

            order = line.order_id
            lines = order.order_line.filtered(lambda l: l.product_id)

            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = (order.total_extra or 0.0) / total_qty

            # ✅ CRITICAL FIX:
            # base = edited price - current extra
            new_base = line.price_unit - extra_per_unit

            line.base_price = new_base