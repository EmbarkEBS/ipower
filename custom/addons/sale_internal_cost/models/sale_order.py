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
    def _onchange_distribute_charges(self):
        """Calculates the charge share per line without overwriting the price."""
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            if not lines:
                continue
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            for line in lines:
                line.internal_charge = extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # This field holds only the extra cost part
    internal_charge = fields.Float(string="Internal Charge", readonly=True)
    
    # We override the price_subtotal to include our charge
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'internal_charge')
    def _compute_amount(self):
        """Override standard subtotal to include the internal charge."""
        super(SaleOrderLine, self)._compute_amount()
        for line in self:
            # Add (Charge * Qty) to the standard subtotal
            charge_amount = line.internal_charge * line.product_uom_qty
            line.price_subtotal += charge_amount
