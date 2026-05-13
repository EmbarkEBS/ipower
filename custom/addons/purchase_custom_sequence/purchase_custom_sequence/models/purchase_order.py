from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_direct_po = fields.Boolean(
        string='Direct Purchase Order'
    )

    @api.model
    def create(self, vals):

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

        return super(PurchaseOrder, self).create(vals)

    def button_confirm(self):

        res = super(PurchaseOrder, self).button_confirm()

        for order in self:

            # Only convert RFQ sequence to PO sequence
            if order.name.startswith('RFQ'):

                order.name = self.env['ir.sequence'].next_by_code(
                    'purchase.order.direct'
                )

        return res
