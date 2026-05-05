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
        string="Total Extra",
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

    @api.onchange('freight', 'duty', 'misc', 'order_line.product_uom_qty')
    def _onchange_distribute_costs(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue

            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty

            for line in lines:
                line.x_internal_charge = extra_per_unit


# =========================
# SALE ORDER LINE
# =========================
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_base_price = fields.Float(
        string="Unit Price",
        digits='Product Price'
    )

    x_internal_charge = fields.Float(
        string="Internal Charge",
        digits='Product Price'
    )

    # -------------------------
    # Set base price on product
    # -------------------------
    @api.onchange('product_id')
    def _onchange_product_id_set_base(self):
        if self.product_id:
            self.x_base_price = self.product_id.lst_price
            self.price_unit = self.x_base_price  # IMPORTANT


    # -------------------------
    # Keep price_unit = base
    # -------------------------
    @api.onchange('x_base_price')
    def _onchange_base_price(self):
        for line in self:
            line.price_unit = line.x_base_price


    # -------------------------
    # CUSTOM AMOUNT COMPUTATION
    # -------------------------
    @api.depends(
        'product_uom_qty',
        'discount',
        'price_unit',
        'tax_id',
        'x_internal_charge'
    )
    def _compute_amount(self):
        for line in self:
            # Base price after discount
            base_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            # Internal charge added ONLY to subtotal
            total_unit_price = base_price + (line.x_internal_charge or 0.0)

            # TAX computed ONLY on base price
            taxes = line.tax_id.compute_all(
                base_price,
                currency=line.order_id.currency_id,
                quantity=line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )

            tax_amount = taxes['total_included'] - taxes['total_excluded']

            line.update({
                'price_subtotal': total_unit_price * line.product_uom_qty,
                'price_tax': tax_amount,
                'price_total': (total_unit_price * line.product_uom_qty) + tax_amount,
            })