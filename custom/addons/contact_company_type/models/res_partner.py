from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    one_time = fields.Boolean(
        string='One Time',
        default=False,
    )
