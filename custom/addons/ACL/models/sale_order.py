from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def action_create_purchase_order(self):
        for order in self:

            po_lines = []

            # ✅ Get default vendor (create one manually if not exists)
            default_vendor = self.env['res.partner'].search(
                [('name', '=', 'Unknown Vendor')], limit=1
            )

            if not default_vendor:
                raise UserError("Please create a vendor named 'Unknown Vendor'")

            vendor = default_vendor  # fallback

            for line in order.order_line:
                product = line.product_id

                if product.type not in ['product', 'consu']:
                    continue

                required_qty = line.product_uom_qty

                if required_qty <= 0:
                    continue

                warehouse = getattr(order, 'warehouse_id', False)

                if warehouse:
                 qty_available = product.with_context(
        warehouse=warehouse.id
    ).free_qty
                else:
                  qty_available = product.free_qty

                # ✅ only check shortage
                if qty_available < required_qty:

                    supplier = product.seller_ids[:1]

                    # ✅ if vendor exists → use it
                    if supplier:
                        vendor = supplier.partner_id

                    # ✅ ALWAYS add line (even if no vendor)
                    po_lines.append((0, 0, {
                        'product_id': product.id,
                        'name': product.name,
                        'product_qty': required_qty - qty_available,
                        'price_unit': supplier.price if supplier else product.standard_price,
                        'date_planned': fields.Datetime.now(),
                    }))

            # ❌ if still empty → real stock available
            if not po_lines:
                raise UserError("All products are in stock.")

            po = self.env['purchase.order'].create({
                'partner_id': vendor.id,
                'origin': order.name,
                'order_line': po_lines,
            })

            return {
                'type': 'ir.actions.act_window',
                'name': 'Purchase Order',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': po.id,
            }