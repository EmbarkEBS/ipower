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
        """Spreads extra costs across all lines and forces subtotal updates."""
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            
            for line in lines:
                # 1. Determine Base (Edited price or Product default)
                base = line.x_base_price if line.x_base_price > 0 else line.product_id.lst_price
                
                # 2. Update Unit Price (Base + Extra)
                line.price_unit = base + extra_per_unit
                
                # 3. Force Subtotal to refresh manually to include the extra charge
                line.price_subtotal = line.price_unit * line.product_uom_qty
                
                # 4. Trigger Odoo's native tax/total calculation
                line._compute_amount()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # This field 'remembers' your edited price (e.g. 1720)
    x_base_price = fields.Float(string="Base Price", digits='Product Price')

    @api.onchange('product_id')
    def _onchange_product_id_set_base(self):
        if self.product_id:
            self.x_base_price = self.product_id.lst_price

    @api.onchange('x_base_price', 'product_uom_qty')
    def _onchange_recompute_all(self):
        """When you edit the Base Price or Quantity, redistribute the global charges."""
        if self.order_id:
            self.order_id._recalculate_line_prices()

    def _prepare_base_line_for_taxes_computation(self):
        """
        THE TAX FIX: Forces the tax engine to use Base Price (1720) 
        instead of Unit Price (1740).
        """
        res = super()._prepare_base_line_for_taxes_computation()
        # Use our stored manual price for the tax math
        tax_base = self.x_base_price if self.x_base_price > 0 else self.price_unit
        res['price_unit'] = tax_base
        return res
