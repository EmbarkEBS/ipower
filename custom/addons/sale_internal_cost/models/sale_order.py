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

    def _compute_extra_distribution(self):
        """
        Distribute extra cost based on quantity
        """
        for order in self:
            lines = order.order_line.filtered(lambda l: l.product_id)

            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = (order.total_extra or 0.0) / total_qty

            for line in lines:
                line.extra_per_unit = extra_per_unit


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    extra_per_unit = fields.Float(string="Extra / Unit", readonly=True)
    extra_total = fields.Monetary(
        string="Extra Total",
        compute="_compute_extra_total",
        store=True
    )

    @api.depends('extra_per_unit', 'product_uom_qty')
    def _compute_extra_total(self):
        for line in self:
            line.extra_total = line.extra_per_unit * line.product_uom_qty

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids', 'extra_total')
    def _compute_amount(self):
        """
        Override Odoo amount calculation to include extra cost
        """
        super()._compute_amount()

        for line in self:
            line.price_subtotal += line.extra_total
            line.price_total += line.extra_total