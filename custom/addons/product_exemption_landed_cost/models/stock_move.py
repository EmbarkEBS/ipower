from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    exemption_rate = fields.Selection(
        [
            ('0', '0%'),
            ('5', '5%'),
        ],
        string="Exemption Rate",
        copy=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('product_id') and not vals.get('exemption_rate'):
                product = self.env['product.product'].browse(vals['product_id'])
                vals['exemption_rate'] = product.product_tmpl_id.exemption_rate
        return super().create(vals_list)
