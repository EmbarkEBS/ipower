from odoo import models, fields

class SaleOrderLineCost(models.Model):
    _name = 'sale.order.line.cost'
    _description = 'Internal Cost Breakdown'

    line_id = fields.Many2one('sale.order.line', required=True, ondelete='cascade')

    cost_type = fields.Selection([
        ('freight', 'Freight'),
        ('duty', 'Duty'),
        ('misc', 'Miscellaneous'),
    ], required=True)

    amount = fields.Float(required=True)
    description = fields.Char()

