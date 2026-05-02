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
                (order.freight or 0.0) +
                (order.duty or 0.0) +
                (order.misc or 0.0)
            )

    def _distribute_extra(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: l.product_id)

            if not lines:
                continue

            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = (order.total_extra or 0.0) / total_qty

            for line in lines:
                line.extra_per_unit = extra_per_unit

    @api.onchange('freight', 'duty', 'misc', 'order_line', 'order_line.product_uom_qty')
    def _onchange_recompute_extra(self):
        self._distribute_extra()