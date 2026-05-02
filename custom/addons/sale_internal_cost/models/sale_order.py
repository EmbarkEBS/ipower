from odoo import models, fields, api


# =========================
# SALE ORDER
# =========================
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

    def _distribute_extra(self):
        """
        Split extra cost based on quantity
        """
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

    @api.depends('order_line.price_total', 'order_line.extra_total')
    def _compute_amount_all(self):
        """
        Add extra cost into order total
        """
        super()._compute_amount_all()

        for order in self:
            extra = sum(order.order_line.mapped('extra_total'))
            order.amount_total += extra


# =========================
# SALE ORDER LINE
# =========================
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    extra_per_unit = fields.Float(string="Extra / Unit")

    extra_total = fields.Monetary(
        string="Extra Total",
        compute="_compute_extra_total",
        store=True
    )

    @api.depends('extra_per_unit', 'product_uom_qty')
    def _compute_extra_total(self):
        for line in self:
            line.extra_total = line.extra_per_unit * line.product_uom_qty