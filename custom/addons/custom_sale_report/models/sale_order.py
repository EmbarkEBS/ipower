from odoo import api, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()

        if self.partner_id.x_studio_incoterm:
            self.incoterm = self.partner_id.x_studio_incoterm

        return res