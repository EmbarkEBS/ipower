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
            order.total_extra = (order.freight or 0.0) + (order.duty or 0.0) + (order.misc or 0.0)

    @api.onchange('freight', 'duty', 'misc')
    def _onchange_extra_costs(self):
        """Triggers recalculation when global charges change."""
        self._recalculate_line_prices()

    def _recalculate_line_prices(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            
            for line in lines:
                # Use stored manual price; if never edited, use product price
                base = line.manual_base_price if line.manual_base_price > 0 else line.product_id.lst_price
                
                # Context flag 'internal_compute' stops the loop in SaleOrderLine
                line.with_context(internal_compute=True).price_unit = base + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Store the actual 'base' price without internal charges
    manual_base_price = fields.Float(string="Base Price", digits='Product Price')

    @api.onchange('price_unit')
    def _onchange_price_unit_catch_manual(self):
        """When you type in the price, calculate and save the 'true' base price."""
        if self._context.get('internal_compute') or not self.order_id:
            return

        for line in self:
            total_qty = sum(line.order_id.order_line.mapped('product_uom_qty')) or 1.0
            extra_per_unit = (line.order_id.total_extra or 0.0) / total_qty
            
            # If user types $110 and extra is $10, we save $100 as the base
            line.manual_base_price = line.price_unit - extra_per_unit

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_recompute_all(self):
        """Ensure charges are redistributed when adding items or changing quantities."""
        if self.order_id:
            # If changing the product entirely, clear the manual memory
            if self._origin.product_id != self.product_id:
                self.manual_base_price = 0.0
            
            # Recalculate everything to redistribute charges
            self.order_id._recalculate_line_prices()
