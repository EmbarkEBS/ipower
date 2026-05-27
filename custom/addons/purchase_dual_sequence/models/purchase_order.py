from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_rfq = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'purchase.rfq'
                ) or 'New'

        return super().create(vals_list)

    def button_confirm(self):

        for order in self:
            if order.is_rfq:
                order.name = self.env['ir.sequence'].next_by_code(
                    'purchase.order.custom'
                )
                order.is_rfq = False

        return super().button_confirm()