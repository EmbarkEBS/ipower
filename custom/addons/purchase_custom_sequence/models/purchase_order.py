from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_direct_po = fields.Boolean(
        string='Direct Purchase Order',
        help='If enabled, PO sequence is generated directly.'
    )
    original_rfq_name = fields.Char(
        string='Original RFQ Number',
        copy=False
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

                rfq_number = self.env['ir.sequence'].next_by_code(
                        'purchase.order.rfq'
                    ) or '/'

                vals['name'] = rfq_number
                vals['original_rfq_name'] = rfq_number

        return super().create(vals_list)

    def button_confirm(self):

        # Call original confirmation
        res = super().button_confirm()

        for order in self:

            # Only convert RFQ to PO
            if not order.is_direct_po:

                # Prevent duplicate conversion
                if 'RFQ' in order.name:

                    # Convert:
                    # IP/RFQ/2025-26/004
                    # to
                    # IP/PO/2025-26/004

                    order.name = order.name.replace(
                        '/RFQ/',
                        '/PO/'
                    )

        return res
    def button_draft(self):

        res = super().button_draft()

        for order in self:

        # Restore RFQ number
         if not order.is_direct_po and order.original_rfq_name:

            order.name = order.original_rfq_name

        return res