from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_direct_po = fields.Boolean(
        string='Direct Purchase Order'
    )

    original_rfq_name = fields.Char(
        string='Original RFQ Number',
        copy=False
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

                rfq_number = self.env['ir.sequence'].next_by_code(
                    'purchase.order.rfq'
                ) or '/'

                vals['name'] = rfq_number
                vals['original_rfq_name'] = rfq_number

        return super().create(vals_list)

    def button_confirm(self):

        res = super().button_confirm()

        for order in self:

            # Only RFQ conversion
            if not order.is_direct_po:

                # Prevent duplicate conversion
                if 'RFQ' in order.name:

                    # Extract running number
                    sequence_number = order.name.split('/')[-1]

                    fiscal_year = order.name.split('/')[2]

                    # Create PO number using same running number
                    po_number = f"IP/PO/{fiscal_year}/{sequence_number}"

                    order.name = po_number

        return res

    def button_draft(self):

        res = super().button_draft()

        for order in self:

            # Restore original RFQ number
            if not order.is_direct_po and order.original_rfq_name:

                order.name = order.original_rfq_name

        return res