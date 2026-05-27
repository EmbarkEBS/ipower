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

    # Confirm PO first
     res = super().button_confirm()

     for order in self:

        # Only RFQ conversion
            if not order.is_direct_po:

            # Prevent duplicate conversion
             if 'RFQ' in order.name:

                old_name = order.name

                # Generate new PO number
                new_name = self.env['ir.sequence'].next_by_code(
                    'purchase.order.direct'
                ) or '/'

                # Update PO number
                order.name = new_name

                # Update related receipts
                pickings = self.env['stock.picking'].search([
                    ('origin', '=', old_name)
                ])

                for picking in pickings:
                    picking.origin = new_name

            return res

