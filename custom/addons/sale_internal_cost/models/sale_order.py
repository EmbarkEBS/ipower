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
        """Calculates the share of extra cost for every line without touching price_unit."""
        for order in self:
            lines = order.order_line.filtered(lambda l: not l.display_type)
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
            extra_per_unit = order.total_extra / total_qty
            for line in lines:
                line.internal_charge = extra_per_unit

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # This field shows the distributed cost share
    internal_charge = fields.Float(string="Int. Charge", readonly=True)
    
    # We create a new subtotal that includes the internal charge for your reference
    price_with_charge = fields.Float(
        string="Total Unit Cost", 
        compute="_compute_price_with_charge"
    )

    @api.depends('price_unit', 'internal_charge')
    def _compute_price_with_charge(self):
        for line in self:
            line.price_with_charge = line.price_unit + line.internal_charge
