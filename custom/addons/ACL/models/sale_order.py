from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_created = fields.Boolean(
        string="Purchase Order Created",
        default=False
    )

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string="Purchase Order"
    )

    def action_create_purchase_order(self):
        self.ensure_one()

        if self.purchase_created:
            raise UserError(
                "Purchase Order already created for this Sales Order."
            )

        # Check if PO already exists
        existing_po = self.env['purchase.order'].search([
            ('origin', '=', self.name)
        ], limit=1)

        if existing_po:
            raise UserError(
                "Purchase Order already exists for this Sales Order."
            )

        # Get products without vendor
        products_without_vendor = self.order_line.filtered(
            lambda l: not l.product_id.seller_ids
        )

        if products_without_vendor:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Select Vendor',
                'res_model': 'sale.vendor.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_sale_order_id': self.id,
                }
            }

        return self._create_purchase_order()

    def _create_purchase_order(self, vendor=False):
        self.ensure_one()

        po_lines = []

        if not vendor:
            first_supplier = self.order_line[0].product_id.seller_ids[:1]
            vendor = first_supplier.partner_id

        for line in self.order_line:

            product = line.product_id

            if product.type not in ['product', 'consu']:
                continue

            po_lines.append((0, 0, {
                'product_id': product.id,
                'name': product.display_name,
                'product_qty': line.product_uom_qty,
                'price_unit': product.standard_price,
                'date_planned': fields.Datetime.now(),
            }))

        if not po_lines:
            raise UserError("No valid products found.")

        po = self.env['purchase.order'].create({
            'partner_id': vendor.id,
            'origin': self.name,
            'order_line': po_lines,
        })

        self.write({
            'purchase_created': True,
            'purchase_order_id': po.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
        }

    def action_view_purchase_order(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': self.purchase_order_id.id,
        }