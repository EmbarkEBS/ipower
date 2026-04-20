from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

<<<<<<< HEAD
    # ✅ Track PO creation
    purchase_created = fields.Boolean(string="Purchase Order Created", default=False)
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
=======
>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25

    def action_create_purchase_order(self):
        for order in self:

<<<<<<< HEAD
            
            if order.purchase_created:
                raise UserError("Purchase Order already created for this Sales Order.")

            po_lines = []

            # ✅ Default vendor fallback
=======
            po_lines = []

            # ✅ Get default vendor (create one manually if not exists)
>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25
            default_vendor = self.env['res.partner'].search(
                [('name', '=', 'Unknown Vendor')], limit=1
            )

            if not default_vendor:
                raise UserError("Please create a vendor named 'Unknown Vendor'")

<<<<<<< HEAD
            vendor = default_vendor
=======
            vendor = default_vendor  # fallback
>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25

            for line in order.order_line:
                product = line.product_id

<<<<<<< HEAD
                # Only stockable / consumable
=======
>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25
                if product.type not in ['product', 'consu']:
                    continue

                required_qty = line.product_uom_qty
<<<<<<< HEAD
=======

>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25
                if required_qty <= 0:
                    continue

                warehouse = getattr(order, 'warehouse_id', False)

                if warehouse:
<<<<<<< HEAD
                    qty_available = product.with_context(
                        warehouse=warehouse.id
                    ).free_qty
                else:
                    qty_available = product.free_qty

                # ✅ shortage only
=======
                 qty_available = product.with_context(
        warehouse=warehouse.id
    ).free_qty
                else:
                  qty_available = product.free_qty

                # ✅ only check shortage
>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25
                if qty_available < required_qty:

                    supplier = product.seller_ids[:1]

<<<<<<< HEAD
                    # If vendor exists → use it
                    if supplier:
                        vendor = supplier.partner_id

=======
                    # ✅ if vendor exists → use it
                    if supplier:
                        vendor = supplier.partner_id

                    # ✅ ALWAYS add line (even if no vendor)
>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25
                    po_lines.append((0, 0, {
                        'product_id': product.id,
                        'name': product.name,
                        'product_qty': required_qty - qty_available,
                        'price_unit': supplier.price if supplier else product.standard_price,
                        'date_planned': fields.Datetime.now(),
                    }))

<<<<<<< HEAD
            if not po_lines:
                raise UserError("All products are in stock.")

            # ✅ Create PO
=======
            # ❌ if still empty → real stock available
            if not po_lines:
                raise UserError("All products are in stock.")

>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25
            po = self.env['purchase.order'].create({
                'partner_id': vendor.id,
                'origin': order.name,
                'order_line': po_lines,
            })

<<<<<<< HEAD
            # ✅ Mark as created
            order.purchase_created = True
            order.purchase_order_id = po.id

=======
>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25
            return {
                'type': 'ir.actions.act_window',
                'name': 'Purchase Order',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': po.id,
<<<<<<< HEAD
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
=======
            }
>>>>>>> 3936c5e7f990485dd18d153535bd814082995d25
