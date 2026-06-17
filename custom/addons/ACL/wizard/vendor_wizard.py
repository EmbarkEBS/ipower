from odoo import models, fields
from odoo.exceptions import UserError


class SaleVendorWizard(models.TransientModel):
    _name = 'sale.vendor.wizard'
    _description = 'Select Vendor'

    sale_order_id = fields.Many2one(
        'sale.order',
        required=True
    )

    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        required=True,
        domain="[('supplier_rank', '>', 0)]"
    )

    def action_confirm(self):
        self.ensure_one()

        if not self.vendor_id:
            raise UserError("Please select a vendor.")

        return self.sale_order_id._create_purchase_order(
            vendor=self.vendor_id
        )