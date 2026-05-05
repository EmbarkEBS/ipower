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
        """Updates Unit Price (Base + Extra) for all lines."""
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            
            for line in lines:
                base = line.x_base_price if line.x_base_price > 0 else line.product_id.lst_price
                # Update price_unit to include charges (This makes 'Amount' correct automatically)
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

    # --- THE TAX FIX: STABLE & CRASH-FREE ---
    def _prepare_base_line_for_taxes_computation(self):
        """
        Forces the tax engine to use x_base_price for math.
        This ignores the extra charges added to price_unit.
        """
        res = super()._prepare_base_line_for_taxes_computation()
        if self.x_base_price > 0:
            res['price_unit'] = self.x_base_price
        return res
