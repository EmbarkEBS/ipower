from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    exemption_rate = fields.Selection(
        [
            ('0', '0%'),
            ('5', '5%'),
        ],
        string="Exemption",
        related="product_id.product_tmpl_id.exemption_rate",
        store=True,
        readonly=False,
    )