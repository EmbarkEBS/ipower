from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight = fields.Monetary(string="Freight", currency_field='currency_id')
    duty = fields.Monetary(string="Duty", currency_field='currency_id')
    misc = fields.Monetary(string="Miscellaneous", currency_field='currency_id')
    
    total_extra = fields.Monetary(
        string="Total Extra Cost", 
        compute="_compute_total_extra", 
        store=True,
        currency_field='currency_id'
    )

    @api.depends('freight', 'duty', 'misc')
    def _compute_total_extra(self):
        for order in self:
            order.total_extra = (order.freight or 0.0) + (order.duty or 0.0) + (order.misc or 0.0)

    @api.onchange('freight', 'duty', 'misc')
    def _onchange_extra_costs(self):
        """Triggered when the global extra charge fields are modified."""
        self._recalculate_line_prices()

    def _recalculate_line_prices(self):
        """Helper method to distribute extra costs across all lines."""
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            
            for line in lines:
                if line.product_id:
                    # Logic: Take the standard product price and add the extra share
                    # This allows the line to reset correctly if freight changes
                    base_price = line.product_id.lst_price
                    line.price_unit = base_price + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_or_qty_apply_extra(self):
        """
        Calculates price when product or quantity changes.
        We don't use super() here to avoid the AttributeError.
        """
        if self.order_id:
            # We wrap this in a call to the parent model to ensure 
            # all lines are updated if the total quantity changes.
            self.order_id._recalculate_line_prices()
