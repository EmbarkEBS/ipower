from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    exemption_rate = fields.Selection(
        [
            ('0', '0%'),
            ('5', '5%'),
        ],
        string="Exemption",
        default='0',
    )