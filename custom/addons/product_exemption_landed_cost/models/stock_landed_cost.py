from odoo import fields, models


class StockValuationAdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    exemption_rate = fields.Selection(
        [
            ('0', '0%'),
            ('5', '5%'),
        ],
        string="Exemption Rate",
        related="move_id.exemption_rate",
        store=True,
        readonly=True,
    )
