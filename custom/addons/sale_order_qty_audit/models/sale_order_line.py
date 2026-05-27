# from odoo import models, api, _

# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     @api.model
#     def write(self, vals):

#         old_values = {
#             line.id: line.product_uom_qty for line in self
#         }

#         res = super().write(vals)

#         if "product_uom_qty" in vals:
#             for line in self:
#                 old_qty = old_values.get(line.id)
#                 new_qty = line.product_uom_qty

#                 if old_qty and old_qty != new_qty:
#                     change_type = "Increased" if new_qty > old_qty else "Decreased"

#                     line.order_id.message_post(
#                         body=_(
#                             "<b>Quantity Changed</b><br/>"
#                             "Product: %s<br/>"
#                             "User: %s<br/>"
#                             "Change: %s<br/>"
#                             "Old Qty: %s<br/>"
#                             "New Qty: %s"
#                         ) % (
#                             line.product_id.display_name,
#                             self.env.user.name,
#                             change_type,
#                             old_qty,
#                             new_qty,
#                         )
#                     )

#         return res

# Quantity modified code working condition
# from odoo import models, api, _

# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     def write(self, vals):

#         old_values = {line.id: line.product_uom_qty for line in self}

#         res = super().write(vals)

#         if "product_uom_qty" in vals:
#             for line in self:
#                 old_qty = old_values.get(line.id)
#                 new_qty = line.product_uom_qty

#                 if old_qty != new_qty:
#                     message = "%s\n%s → %s" % (
#                         line.product_id.name,
#                         old_qty,
#                         new_qty
#                     )

#                     line.order_id.message_post(body=message)

#         return res

from odoo import models, api, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, vals):

        old_values = {}
        for line in self:
            old_values[line.id] = {
                "qty": line.product_uom_qty,
                "price": line.price_unit,
                "discount": line.discount,
            }

        res = super().write(vals)

        tracked_fields = any(
            f in vals for f in ["product_uom_qty", "price_unit", "discount"]
        )

        if tracked_fields:
            for line in self:
                old = old_values.get(line.id)
                if not old:
                    continue

                messages = []

                # -------------------------
                # QUANTITY CHANGE
                # -------------------------
                if "product_uom_qty" in vals:
                    new_qty = line.product_uom_qty
                    if old["qty"] != new_qty:
                        arrow = "↑" if new_qty > old["qty"] else "↓"

                        messages.append(
                            "Qty: %s %s %s"
                            % (old["qty"], arrow, new_qty)
                        )

                # -------------------------
                # PRICE CHANGE
                # -------------------------
                if "price_unit" in vals:
                    new_price = line.price_unit
                    if old["price"] != new_price:
                        arrow = "↑" if new_price > old["price"] else "↓"

                        messages.append(
                            "Price: %s %s %s"
                            % (old["price"], arrow, new_price)
                        )

                # -------------------------
                # DISCOUNT CHANGE
                # -------------------------
                if "discount" in vals:
                    new_discount = line.discount
                    if old["discount"] != new_discount:
                        arrow = "↑" if new_discount > old["discount"] else "↓"

                        messages.append(
                            "Discount: %s%% %s %s%%"
                            % (old["discount"], arrow, new_discount)
                        )

                # -------------------------
                # POST TO CHATTER
                # -------------------------
                if messages:
                    body = "%s\n%s" % (
                        line.product_id.name,
                        "\n".join(messages),
                    )

                    line.order_id.message_post(
                        body=body,
                        subtype_xmlid="mail.mt_note"
                    )

        return res
