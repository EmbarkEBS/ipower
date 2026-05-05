from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    internal_cost_ids = fields.One2many(
        'sale.order.line.cost',
        'line_id',
        string="Internal Costs"
    )

    total_internal_cost = fields.Float(
        compute='_compute_internal_cost',
        store=True
    )

    price_without_cost = fields.Float(string="Base Price")
    is_manual_price = fields.Boolean(string="Manual Price Override")

    @api.depends('internal_cost_ids.amount')
    def _compute_internal_cost(self):
        for line in self:
            line.total_internal_cost = sum(line.internal_cost_ids.mapped('amount'))

    @api.onchange('product_id')
    def _set_base_price(self):
        for line in self:
            if line.product_id:
                line.price_without_cost = line.product_id.lst_price
                if not line.is_manual_price:
                    line.price_unit = line.price_without_cost + line.total_internal_cost

    @api.onchange('internal_cost_ids')
    def _update_price_with_cost(self):
        for line in self:
            if not line.is_manual_price:
                line.price_unit = line.price_without_cost + line.total_internal_cost

