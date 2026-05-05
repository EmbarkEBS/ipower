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
        """Redistribute when global costs change."""
        self._recalculate_line_prices()

    def _recalculate_line_prices(self):
        """Core logic to distribute costs across lines."""
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            
            for line in lines:
                base = line.x_base_price if line.x_base_price > 0 else line.product_id.lst_price
                # Update price_unit and MANUALLY trigger the subtotal computation
                line.price_unit = base + extra_per_unit
                line._compute_amount()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_base_price = fields.Float(string="Base Price", digits='Product Price')

    @api.onchange('product_id')
    def _onchange_product_id_set_base(self):
        if self.product_id:
            # Setting initial base price from product list price
            self.x_base_price = self.product_id.lst_price

    @api.onchange('x_base_price', 'product_uom_qty')
    def _onchange_line_recompute_all(self):
        """When a line changes, update the whole order distribution."""
        if self.order_id:
            self.order_id._recalculate_line_prices()

    # --- THE TAX FIX ---
    def _prepare_base_line_for_taxes_computation(self):
        """Ensures taxes only see the Base Price."""
        res = super()._prepare_base_line_for_taxes_computation()
        if self.x_base_price > 0:
            res['price_unit'] = self.x_base_price
        return res

    # --- THE AMOUNT/SUBTOTAL FIX ---
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Forces the subtotal to recalculate using the new price_unit.
        We call the standard Odoo logic to ensure it's accurate.
        """
        super(SaleOrderLine, self)._compute_amount()
