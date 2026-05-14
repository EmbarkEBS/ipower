from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_direct_po = fields.Boolean(
        string='Direct Purchase Order',
        help='If enabled, PO sequence is generated directly.'
    )

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            # Skip if name already exists
            if vals.get('name', '/') != '/':
                continue

            # Direct Purchase Order
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

        # Call original confirmation
        res = super().button_confirm()

        for order in self:

            # Only convert RFQ to PO
            if not order.is_direct_po:

                # Prevent duplicate conversion
                if 'RFQ' in order.name:

                    order.name = self.env['ir.sequence'].next_by_code(
                        'purchase.order.direct'
                    ) or '/'

        return res