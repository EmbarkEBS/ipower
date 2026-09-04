from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(
        selection_add=[
            ('one_time', 'One Time'),
        ],
        ondelete={
            'one_time': 'set null',
        },
    )
