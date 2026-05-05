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

    @api.onchange('freight', 'duty', 'misc', 'total_extra')
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
                # Use Product Cost Price (standard_price) as the base
                base = line.product_id.standard_price or 0.0
                line.price_unit = base + extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_recompute_price(self):
        if self.order_id:
            self.order_id._recalculate_line_prices()

    def _prepare_base_line_for_taxes_computation(self):
        """
        Force the tax engine to use the Cost Price (standard_price) 
        as the tax base, effectively applying 0% tax to the internal charge.
        """
        res = super()._prepare_base_line_for_taxes_computation()
        if self.product_id:
            res['price_unit'] = self.product_id.standard_price
        return res
