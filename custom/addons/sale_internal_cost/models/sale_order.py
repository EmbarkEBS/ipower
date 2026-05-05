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
        """Distribute charges when global fields change."""
        self._recalculate_line_prices()

    def _recalculate_line_prices(self):
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            for line in lines:
                line.x_internal_charge = extra_per_unit
                # Explicitly update price_unit so Amount recalculates
                base = line.x_base_price if line.x_base_price > 0 else line.product_id.lst_price
                line.price_unit = base + line.x_internal_charge

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_base_price = fields.Float(string="Unit Price (Base)", digits='Product Price')
    x_internal_charge = fields.Float(string="Int. Charge", readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id_set_base(self):
        if self.product_id:
            self.x_base_price = self.product_id.lst_price

    @api.onchange('x_base_price', 'product_uom_qty')
    def _onchange_recompute_all(self):
        """Redistribute charges if base price or quantity changes."""
        if self.order_id:
            self.order_id._recalculate_line_prices()

    # --- CRITICAL FIX FOR AMOUNT ---
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Forces the 'Amount' column to follow price_unit (Base + Charges).
        Odoo's native method is called first, then we ensure our total is correct.
        """
        super(SaleOrderLine, self)._compute_amount()
        for line in self:
            # This ensures Amount = (1720 + 20) * 1 = 1740
            line.price_subtotal = line.price_unit * line.product_uom_qty
            line.price_total = line.price_subtotal + line.price_tax

    # --- CRITICAL FIX FOR TAX ---
    def _prepare_base_line_for_taxes_computation(self):
        """
        Forces Taxes to look only at x_base_price (1720).
        """
        res = super()._prepare_base_line_for_taxes_computation()
        if self.x_base_price > 0:
            res['price_unit'] = self.x_base_price
        return res
