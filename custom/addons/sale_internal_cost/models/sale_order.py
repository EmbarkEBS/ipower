class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_recompute_price(self):
        if self.order_id:
            self.order_id._recalculate_line_prices()

    def _prepare_base_line_for_taxes_computation(self):
        """
        Tell the tax engine to calculate tax ONLY on the cost.
        Example: Tax = 215.00 * 5% = 10.75
        """
        res = super()._prepare_base_line_for_taxes_computation()
        if self.product_id:
            res['price_unit'] = self.product_id.standard_price
        return res

    @api.depends('price_unit', 'product_uom_qty', 'tax_id')
    def _compute_amount(self):
        """
        Override subtotal computation to ensure it shows (Unit Price * Qty)
        while the tax engine (handled above) uses only the Cost.
        """
        super()._compute_amount()
        for line in self:
            # Force subtotal to reflect the price the customer sees (Cost + Extra)
            line.price_subtotal = line.price_unit * line.product_uom_qty
