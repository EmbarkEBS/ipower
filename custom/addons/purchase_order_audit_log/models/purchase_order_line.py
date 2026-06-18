from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, vals):

        old_values = {}
        for line in self:
            old_values[line.id] = {
                "qty": line.product_qty,
                "price": line.price_unit,
                "discount": getattr(line, "discount", 0.0),
            }

        res = super().write(vals)

        tracked_fields = any(
            f in vals for f in ["product_qty", "price_unit", "discount"]
        )

        if tracked_fields:
            for line in self:
                old = old_values.get(line.id)
                if not old:
                    continue

                messages = []

                # Quantity
                if "product_qty" in vals:
                    new_qty = line.product_qty
                    if old["qty"] != new_qty:
                        arrow = "↑" if new_qty > old["qty"] else "↓"
                        messages.append(
                            "Qty: %s %s %s"
                            % (old["qty"], arrow, new_qty)
                        )

                # Price
                if "price_unit" in vals:
                    new_price = line.price_unit
                    if old["price"] != new_price:
                        arrow = "↑" if new_price > old["price"] else "↓"
                        messages.append(
                            "Price: %s %s %s"
                            % (old["price"], arrow, new_price)
                        )

                # Discount (only if field exists)
                if "discount" in vals and hasattr(line, "discount"):
                    new_discount = line.discount
                    if old["discount"] != new_discount:
                        arrow = (
                            "↑"
                            if new_discount > old["discount"]
                            else "↓"
                        )
                        messages.append(
                            "Discount: %s%% %s %s%%"
                            % (
                                old["discount"],
                                arrow,
                                new_discount,
                            )
                        )

                if messages:
                    body = "%s\n%s" % (
                        line.product_id.name,
                        "\n".join(messages),
                    )

                    line.order_id.message_post(
                        body=body,
                        subtype_xmlid="mail.mt_note",
                    )

        return res