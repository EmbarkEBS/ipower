from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    incoterm_location = fields.Char(string="Incoterm Location")
