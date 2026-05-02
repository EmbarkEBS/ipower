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
        """When extra costs change, distribute them across lines."""
        self._recalculate_line_prices()

    def _recalculate_line_prices(self):
        for order in self:
            lines = order.order_line
            if not lines:
                continue
            
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            
            for line in lines:
                # We use the current price_unit if it exists, 
                # or the product's list price if it's a new line
                base = line.product_id.lst_price
                line.price_unit = base + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # We trigger the recalculation when quantity changes to redistribute the cost
    @api.onchange('product_uom_qty')
    def _onchange_qty_recompute_extra(self):
        if self.order_id:
            self.order_id._recalculate_line_prices()
            
    # Remove the overwrite on product_id change or ensure it doesn't loop
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.order_id:
            self.order_id._recalculate_line_prices()
        return res
