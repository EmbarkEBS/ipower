from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ✅ Fields to track PO
    purchase_created = fields.Boolean(string="Purchase Created", default=False)
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")

    def action_create_purchase_order(self):
        self.ensure_one()  # ✅ single record only

        # ❌ Prevent duplicate
        if self.purchase_created:
            raise UserError("Purchase Order already created for this Sales Order.")

        po_lines = []

        # ✅ Default vendor
        vendor = self.env['res.partner'].search(
            [('name', '=', 'Unknown Vendor')], limit=1
        )

        if not vendor:
            raise UserError("Please create a vendor named 'Unknown Vendor'")

        for line in self.order_line:
            product = line.product_id

            # Only stockable / consumable
            if product.type not in ['product', 'consu']:
                continue

            required_qty = line.product_uom_qty
            if required_qty <= 0:
                continue

            # Stock check
            if self.warehouse_id:
                qty_available = product.with_context(
                    warehouse=self.warehouse_id.id
                ).free_qty
            else:
                qty_available = product.free_qty

            # Only shortage
            if qty_available < required_qty:

                supplier = product.seller_ids[:1]

                if supplier:
                    vendor = supplier.partner_id

                po_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': product.name,
                    'product_qty': required_qty - qty_available,
                    'price_unit': supplier.price if supplier else product.standard_price,
                    'date_planned': fields.Datetime.now(),
                }))

        if not po_lines:
            raise UserError("All products are in stock.")

        # ✅ Create PO
        po = self.env['purchase.order'].create({
            'partner_id': vendor.id,
            'origin': self.name,
            'order_line': po_lines,
        })

        # ✅ IMPORTANT → use write()
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
        }