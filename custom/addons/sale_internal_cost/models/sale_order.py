from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight = fields.Monetary(string="Freight")
    duty = fields.Monetary(string="Duty")
    misc = fields.Monetary(string="Miscellaneous")

    total_extra = fields.Monetary(
        string="Total Extra Cost",
        compute="_compute_total_extra",
        store=True
    )

    @api.depends('freight', 'duty', 'misc')
    def _compute_total_extra(self):
        for order in self:
            order.total_extra = (
                (order.freight or 0.0) +
                (order.duty or 0.0) +
                (order.misc or 0.0)
            )

    @api.onchange('freight', 'duty', 'misc')
    def _onchange_apply_extra_cost(self):
        """
        Apply extra cost ONLY when extra fields change.
        Do NOT override manually edited lines.
        """
        for order in self:
            lines = order.order_line.filtered(lambda l: l.product_id)

            if not lines:
                continue

            total_extra = order.total_extra or 0.0
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0

            extra_per_unit = total_extra / total_qty

            for line in lines:
                if not line.is_manual_price:
                    base_price = line.product_id.lst_price
                    line.price_unit = base_price + extra_per_unit


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_manual_price = fields.Boolean(string="Manual Price", default=False)

    @api.onchange('price_unit')
    def _onchange_price_unit_manual(self):
        """
        Mark line as manual ONLY if user changes price
        (avoid marking during system updates)
        """
        for line in self:
            if line.product_id:
                # Mark manual ONLY if price differs from computed price
                order = line.order_id
                if not order:
                    continue

                lines = order.order_line.filtered(lambda l: l.product_id)
                total_extra = order.total_extra or 0.0
                total_qty = sum(lines.mapped('product_uom_qty')) or 1.0
                extra_per_unit = total_extra / total_qty

                expected_price = line.product_id.lst_price + extra_per_unit

                # Only mark manual if user really changed it
                if abs(line.price_unit - expected_price) > 0.0001:
                    line.is_manual_price = True

    @api.onchange('product_id')
    def _onchange_product_apply_extra(self):
        """
        Apply price ONLY when product is selected.
        Do NOT reapply on quantity change.
        """
        for line in self:
            order = line.order_id
            if not order or not line.product_id:
                continue

            lines = order.order_line.filtered(lambda l: l.product_id)

            total_extra = order.total_extra or 0.0
            total_qty = sum(lines.mapped('product_uom_qty')) or 1.0

            extra_per_unit = total_extra / total_qty

            # Apply only if NOT manual
            if not line.is_manual_price:
                base_price = line.product_id.lst_price
                line.price_unit = base_price + extra_per_unit