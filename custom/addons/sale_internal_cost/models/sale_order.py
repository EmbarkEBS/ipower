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
        self._recalculate_line_prices()

    def _recalculate_line_prices(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            
            for line in lines:
                # Use manual_price if set, otherwise fallback to product price
                base = line.manual_price if line.manual_price > 0 else line.product_id.lst_price
                line.price_unit = base + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # New field to store your manual edits
    manual_price = fields.Float(string="Base Price (Manual)")

    @api.onchange('price_unit')
    def _onchange_price_unit_manual(self):
        """
        If the user manually changes the price, we subtract the 
        current extra cost share to store the 'true' base price.
        """
        # Avoid recursion: only run if the user is physically typing
        if self._context.get('import_file'): 
            return

        total_qty = sum(self.order_id.order_line.mapped('product_uom_qty')) or 1.0
        extra_per_unit = (self.order_id.total_extra or 0.0) / total_qty
        
        # Store what the price would be WITHOUT the extra charge
        self.manual_price = self.price_unit - extra_per_unit

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_or_qty_apply_extra(self):
        if self.order_id:
            self.order_id._recalculate_line_prices()
