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
                line._update_price_unit()


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
        for line in self:
            if line.product_id:
                line.x_base_price = line.product_id.lst_price
                line._update_price_unit()

    # -------------------------
    # Update price_unit (UI)
    # -------------------------
    @api.onchange('x_base_price', 'x_internal_charge')
    def _update_price_unit(self):
        for line in self:
            line.price_unit = (line.x_base_price or 0.0) + (line.x_internal_charge or 0.0)

    # -------------------------
    # 🔥 CRITICAL FIX
    # -------------------------
    def _prepare_base_line_for_taxes_computation(self):
        """
        This controls what Odoo uses for:
        - subtotal
        - tax
        - total
        """

        res = super()._prepare_base_line_for_taxes_computation()

        base_price = self.x_base_price or 0.0
        charge = self.x_internal_charge or 0.0
        qty = self.product_uom_qty or 0.0

        # ✅ TAX → ONLY base price
        res['price_unit'] = base_price

        # ✅ SUBTOTAL → include internal charge
        res['price_subtotal'] = (base_price + charge) * qty

        return res