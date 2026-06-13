from odoo import fields, models


class StockValuationAdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    exemption_rate = fields.Selection(
        [
            ('0', '0%'),
            ('5', '5%'),
        ],
        string="Exemption",
        compute="_compute_exemption_rate",
        store=True,
    )

    def _compute_exemption_rate(self):
        for line in self:
            line.exemption_rate = (
                line.product_id.product_tmpl_id.exemption_rate
                if line.product_id
                else False
            )