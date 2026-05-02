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
        """Triggers when global costs change"""
        self._recalculate_line_prices()

    def _recalculate_line_prices(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            
            for line in lines:
                # 1. Use the manual price if the user typed one
                # 2. Otherwise use the product list price
                base = line.x_manual_price if line.x_manual_price > 0 else line.product_id.lst_price
                
                # Update the unit price with the extra cost
                line.price_unit = base + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # This field is the "Master" for your manual edits
    x_manual_price = fields.Float(string="Manual Base Price", digits='Product Price')

    @api.onchange('product_id')
    def _onchange_product_id_reset_manual(self):
        """Reset manual price when product changes"""
        self.x_manual_price = self.product_id.lst_price

    @api.onchange('x_manual_price', 'product_uom_qty')
    def _onchange_manual_price_trigger(self):
        """When you edit the MANUAL price field, update the real Unit Price"""
        if self.order_id:
            self.order_id._recalculate_line_prices()

    # NOTE: We stop using @api.onchange('price_unit') because it loops with Odoo's core
