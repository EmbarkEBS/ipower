from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_created = fields.Boolean(string="Purchase Order Created", default=False)
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")

    def action_create_purchase_order(self):
        for order in self:

            # جلوگیری از duplicate
            if order.purchase_created:
                raise UserError("Purchase Order already created for this Sales Order.")

            po_lines = []

            # Default vendor fallback
            default_vendor = self.env['res.partner'].search(
                [('name', '=', 'Unknown Vendor')], limit=1
            )

            if not default_vendor:
                raise UserError("Please create a vendor named 'Unknown Vendor'")

            vendor = default_vendor

            for line in order.order_line:
                product = line.product_id

                # Only stockable / consumable
                if product.type not in ['product', 'consu']:
                    continue

                required_qty = line.product_uom_qty
                if required_qty <= 0:
                    continue

                supplier = product.seller_ids[:1]

                # اگر vendor داشت استفاده کن
                if supplier:
                    vendor = supplier.name   # ✅ FIX (not partner_id)

                po_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': product.name,
                    'product_qty': required_qty,   # ✅ FULL QTY (no stock check)
                    'price_unit': supplier.price if supplier else product.standard_price,
                    'date_planned': fields.Datetime.now(),
                }))

            if not po_lines:
                raise UserError("No valid products to purchase.")

            # Create PO
            po = self.env['purchase.order'].create({
                'partner_id': vendor.id,
                'origin': order.name,
                'order_line': po_lines,
            })

            order.purchase_created = True
            order.purchase_order_id = po.id

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