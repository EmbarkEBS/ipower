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
                line.x_internal_charge = extra_per_unit
                # Update the unit price to include charges
                base = line.x_base_price if line.x_base_price > 0 else line.product_id.lst_price
                line.price_unit = base + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_base_price = fields.Float(string="Base Price", digits='Product Price')
    x_internal_charge = fields.Float(string="Int. Charge", readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id_set_base(self):
        if self.product_id:
            self.x_base_price = self.product_id.lst_price

    @api.onchange('x_base_price', 'product_uom_qty')
    def _onchange_recompute_all(self):
        if self.order_id:
            self.order_id._recalculate_line_prices()

    # --- CRITICAL FIX FOR SUBTOTAL AND TAX ---
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids', 'x_base_price')
    def _compute_amount(self):
        """
        Forces the 'Amount' column to include charges,
        but calculates the 'Tax' using ONLY the base price.
        """
        for line in self:
            # 1. Use Base Price for tax math
            tax_base = line.x_base_price if line.x_base_price > 0 else line.product_id.lst_price
            
            # 2. Compute taxes manually based on the base price
            taxes = line.tax_id.compute_all(
                tax_base, 
                line.order_id.currency_id, 
                line.product_uom_qty, 
                product=line.product_id, 
                partner=line.order_id.partner_shipping_id
            )
            
            # 3. Apply the custom results
            # Subtotal (Amount column) = Price with Charges * Qty
            line.price_subtotal = line.price_unit * line.product_uom_qty
            
            # Tax = Tax on Base only
            line.price_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            
            # Total = Subtotal + Tax
            line.price_total = line.price_subtotal + line.price_tax
