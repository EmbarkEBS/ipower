from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight = fields.Monetary(string="Freight")
    duty = fields.Monetary(string="Duty")
    misc = fields.Monetary(string="Miscellaneous")
    total_extra = fields.Monetary(string="Total Extra", compute="_compute_total_extra", store=True)

    @api.depends('freight', 'duty', 'misc')
    def _compute_total_extra(self):
        for order in self:
            order.total_extra = (order.freight or 0.0) + (order.duty or 0.0) + (order.misc or 0.0)

    @api.onchange('freight', 'duty', 'misc')
    def _onchange_extra_costs(self):
        self._recalculate_line_prices()

    def _recalculate_line_prices(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            for line in lines:
                base = line.x_base_price if line.x_base_price > 0 else line.product_id.lst_price
                line.price_unit = base + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_base_price = fields.Float(string="Base Price", digits='Product Price')

    @api.onchange('product_id')
    def _onchange_product_id_set_base(self):
        if self.product_id:
            self.x_base_price = self.product_id.lst_price

    @api.onchange('x_base_price', 'product_uom_qty')
    def _onchange_recompute_all(self):
        if self.order_id:
            self.order_id._recalculate_line_prices()

    # --- THE FIX FOR BUG 1 (Amount) & BUG 2 (Tax) ---
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'x_base_price')
    def _compute_amount(self):
        """
        Force Odoo to calculate the Subtotal (Amount) using price_unit (220)
        but calculate the Tax using x_base_price (200).
        """
        for line in self:
            # 1. Calculate the Subtotal (The 'Amount' column)
            # This ensures Amount = 220 * Qty
            line.price_subtotal = line.price_unit * line.product_uom_qty
            
            # 2. Calculate the Tax (Only on the Base Price)
            # We use x_base_price to find the tax amount
            tax_base = line.x_base_price if line.x_base_price > 0 else line.price_unit
            taxes = line.tax_id.compute_all(
                tax_base, 
                line.order_id.currency_id, 
                line.product_uom_qty, 
                product=line.product_id, 
                partner=line.order_id.partner_shipping_id
            )
            
            line.price_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            line.price_total = line.price_subtotal + line.price_tax
