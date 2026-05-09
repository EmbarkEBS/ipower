from odoo import models, fields


class QuotationDocument(models.Model):
    _inherit = 'quotation.document'

    quotation_template_ids = fields.Many2many(
        groups='custom_sale_security.group_custom_sale_user'
    )