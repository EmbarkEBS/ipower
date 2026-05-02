from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight = fields.Monetary(string="Freight")
    duty = fields.Monetary(string="Duty")
    misc = fields.Monetary(string="Miscellaneous")
    total_extra = fields.Monetary(string="Total Extra Cost", compute="_compute_total_extra", store=True)

    @api.depends('freight', 'duty', 'misc')
    def _compute_total_extra(self):
        for order in self:
            order.total_extra = (order.freight or 0.0) + (order.duty or 0.0) + (order.misc or 0.0)

    @api.onchange('freight', 'duty', 'misc')
    def _onchange_extra_costs(self):
        """Redistribute charges when global extra cost fields change."""
        self._recalculate_line_prices()

    def _recalculate_line_prices(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            
            for line in lines:
                # Priority 1: User's manual edit
                # Priority 2: Product default price
                base = line.manual_price if line.manual_price > 0 else line.product_id.lst_price
                # We use 'with_context' to tell the line 'DO NOT trigger manual price update'
                line.with_context(from_recompute=True).price_unit = base + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # This field remembers what you typed BEFORE the extra charges were added
    manual_price = fields.Float(string="Base Price (Manual)", digits='Product Price')

    @api.onchange('price_unit')
    def _onchange_price_unit_manual(self):
        """Captures your manual edit and saves it as the new base price."""
        # If this onchange was triggered by our own code re-calculating, skip it.
        if self._context.get('from_recompute'):
            return

        for line in self:
            if not line.order_id:
                continue
            
            # Calculate what the share of extra cost is right now
            total_qty = sum(line.order_id.order_line.mapped('product_uom_qty')) or 1.0
            extra_per_unit = (line.order_id.total_extra or 0.0) / total_qty
            
            # Save the 'true' base price (what you typed - the extra charge)
            line.manual_price = line.price_unit - extra_per_unit

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_or_qty_apply_extra(self):
        """Ensures price is correct when adding new items or changing quantities."""
        if self.order_id:
            # If changing the product, reset the manual price so it fetches the new product's price
            if 'product_id' in self._onchange_methods:
                 self.manual_price = 0.0
            self.order_id._recalculate_line_prices()
