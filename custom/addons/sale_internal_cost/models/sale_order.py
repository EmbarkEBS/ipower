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

    @api.onchange('freight', 'duty', 'misc', 'order_line.product_uom_qty')
    def _onchange_distribute_costs(self):
        """Calculates charge share and updates all lines."""
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            for line in lines:
                line.x_internal_charge = extra_per_unit
                # Force the Price + Charges field and Subtotal to update
                line.price_unit = line.x_base_price + line.x_internal_charge

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_base_price = fields.Float(string="Unit Price", digits='Product Price')
    x_internal_charge = fields.Float(string="Int. Charge", readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id_set_base(self):
        if self.product_id:
            self.x_base_price = self.product_id.lst_price

    @api.onchange('x_base_price', 'x_internal_charge', 'product_uom_qty')
    def _onchange_update_subtotal(self):
        """Forces the 'Amount' column to include charges in the UI."""
        for line in self:
            line.price_unit = line.x_base_price + line.x_internal_charge
            # Recalculates 'Amount' using the new Price + Charges
            line.price_subtotal = line.price_unit * line.product_uom_qty

    def _prepare_base_line_for_taxes_computation(self):
        """THE TAX FIX: Forces VAT (86.00) to be calculated on Base (1720) only."""
        res = super()._prepare_base_line_for_taxes_computation()
        if self.x_base_price > 0:
            res['price_unit'] = self.x_base_price
        return res
