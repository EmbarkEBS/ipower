from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_direct_po = fields.Boolean(
        string='Direct Purchase Order'
    )

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            # Skip if already has name
            if vals.get('name', '/') != '/':
                continue

            # Direct PO
            if vals.get('is_direct_po'):

                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'purchase.order.direct'
                ) or '/'

                # RFQ
            else:

                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'purchase.order.rfq'
                ) or '/'

                return super().create(vals_list)

    def button_confirm(self):

        res = super(PurchaseOrder, self).button_confirm()

        for order in self:

            # Only convert RFQ sequence to PO sequence
            if order.name.startswith('RFQ'):

                order.name = self.env['ir.sequence'].next_by_code(
                    'purchase.order.direct'
                )

        return res
