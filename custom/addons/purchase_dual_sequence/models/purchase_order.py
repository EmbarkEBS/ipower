from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_rfq = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'purchase.rfq'
            ) or 'New'

        return super().create(vals)

    def button_confirm(self):
        for order in self:
            if order.is_rfq:
                order.name = self.env['ir.sequence'].next_by_code(
                    'purchase.order.custom'
                )
                order.is_rfq = False

        return super().button_confirm()