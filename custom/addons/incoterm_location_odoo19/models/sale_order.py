from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # incoterm_location = fields.Char(string="Incoterm Location")

    @api.onchange("partner_id")
    def _onchange_partner_incoterm_location(self):
        if self.partner_id:
            self.incoterm_location = self.partner_id.incoterm_location
