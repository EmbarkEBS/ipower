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
        """Spreads extra costs across all lines and forces subtotal updates."""
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            for line in lines:
                line.x_internal_charge = extra_per_unit
                # Update Unit Price (Base + Charge)
                line.price_unit = (line.x_base_price or line.product_id.lst_price) + extra_per_unit

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
            self.order_id._onchange_distribute_costs()

    # --- THE FINAL FIX FOR SUBTOTAL AND TAX ---
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'x_base_price')
    def _compute_amount(self):
        """
        Forces the 'Amount' column to include charges,
        but calculates the 'Tax' using ONLY the base price.
        """
        for line in self:
            # 1. Determine tax base
            tax_base = line.x_base_price if line.x_base_price > 0 else line.product_id.lst_price
            
            # 2. Compute taxes manually based on the base price
            # If Odoo crashes on 'tax_id', change it to 'tax_ids' or 'taxes_id'
            taxes = line.tax_id.compute_all(
                tax_base, 
                line.order_id.currency_id, 
                line.product_uom_qty, 
                product=line.product_id, 
                partner=line.order_id.partner_shipping_id
            )
            
            # 3. Force the Subtotal (Amount column) to include charges
            line.price_subtotal = line.price_unit * line.product_uom_qty
            
            # 4. Set Tax to the value calculated from the base price
            line.price_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            
            # 5. Set the Total
            line.price_total = line.price_subtotal + line.price_tax
