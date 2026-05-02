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

    @api.onchange('freight', 'duty', 'misc', 'order_line')
    def _onchange_apply_extra_cost(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: l.product_id)
            if not lines:
                continue

            total_extra = order.total_extra or 0.0
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0

            extra_per_unit = total_extra / total_qty

            for line in lines:

                # STEP 1: remove old extra (if any)
                if hasattr(line, '_old_extra'):
                    line.price_unit -= line._old_extra

                # STEP 2: apply new extra
                line.price_unit += extra_per_unit

                # STEP 3: store applied extra
                line._old_extra = extra_per_unit


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_apply_extra(self):
        if not self.order_id:
            return

        order = self.order_id
        lines = order.order_line.filtered(lambda l: l.product_id)

        if not lines:
            return

        total_extra = order.total_extra or 0.0
        total_qty = sum(lines.mapped('product_uom_qty')) or 1.0

        extra_per_unit = total_extra / total_qty

        for line in lines:

            # remove old extra
            if hasattr(line, '_old_extra'):
                line.price_unit -= line._old_extra

            # add new extra
            line.price_unit += extra_per_unit

            line._old_extra = extra_per_unit