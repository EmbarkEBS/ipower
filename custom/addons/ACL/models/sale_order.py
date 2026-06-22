from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        domain=[('supplier_rank', '>', 0)]
    )

    purchase_created = fields.Boolean(
        string='Purchase Order Created',
        default=False
    )

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order'
    )

    def action_create_purchase_order(self):
        self.ensure_one()

        # Prevent duplicate PO
        if self.purchase_created:
            raise UserError(
                "Purchase Order already created for this Sales Order."
            )

        # Vendor required
        if not self.vendor_id:
            raise UserError(
                "Please select a Vendor before creating a Purchase Order."
            )

        vendor = self.vendor_id
        po_lines = []

        for line in self.order_line:
            product = line.product_id

            # Only stockable and consumable products
            if product.type not in ['product', 'consu']:
                continue

            required_qty = line.product_uom_qty

            if required_qty <= 0:
                continue

            warehouse = self.warehouse_id

            if warehouse:
                qty_available = product.with_context(
                    warehouse=warehouse.id
                ).free_qty
            else:
                qty_available = product.free_qty

            # Create PO only for shortage quantity
            if qty_available < required_qty:

                shortage_qty = required_qty - qty_available

                supplier = product.seller_ids[:1]

                po_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': product.display_name,
                    'product_qty': shortage_qty,
                    'price_unit': (
                        supplier.price
                        if supplier
                        else product.standard_price
                    ),
                    'date_planned': fields.Datetime.now(),
                }))

        if not po_lines:
            raise UserError(
                "All products are available in stock."
            )

        # IMPORTANT:
        # Keep standard PO create call unchanged
        # so your custom purchase sequence module can work.
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
            'name': 'Purchase Order',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
            'target': 'current',
        }

    def action_view_purchase_order(self):
        self.ensure_one()

        if not self.purchase_order_id:
            raise UserError("No Purchase Order found.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': self.purchase_order_id.id,
            'target': 'current',
        }