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
                # If you edited the price, we use that as the base. 
                # Otherwise, we use the product's default list price.
                base = line.manual_price if line.manual_price > 0 else line.product_id.lst_price
                
                # 'from_recompute' prevents our own onchange from 'stealing' this update
                line.with_context(from_recompute=True).price_unit = base + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Remembers your manual entry before charges were added
    manual_price = fields.Float(string="Base Price (Manual)", digits='Product Price')

    @api.onchange('price_unit')
    def _onchange_price_unit_manual(self):
        """When you type a price, we calculate what the base 'non-charge' price is."""
        if self._context.get('from_recompute') or not self.order_id:
            return

        total_qty = sum(self.order_id.order_line.mapped('product_uom_qty')) or 1.0
        extra_per_unit = (self.order_id.total_extra or 0.0) / total_qty
        
        # Save your manual price MINUS the current internal charge share
        self.manual_price = self.price_unit - extra_per_unit

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_or_qty_apply_extra(self):
        """Ensures price is correct when changing items or quantities."""
        if self.order_id:
            # If the user changed the actual PRODUCT, reset the manual memory
            if self._origin.product_id != self.product_id:
                self.manual_price = 0.0
            self.order_id._recalculate_line_prices()
