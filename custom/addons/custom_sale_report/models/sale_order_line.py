from odoo import models, api
from datetime import timedelta

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _update_expected_delivery(self):
        for line in self:
            if line.order_id.date_order:
                line.x_studio_expected_delivery_2 = (
                    line.order_id.date_order.date()
                    + timedelta(days=int(line.customer_lead or 0))
                )
            else:
                line.x_studio_expected_delivery_2 = False

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._update_expected_delivery()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if 'customer_lead' in vals or 'product_id' in vals:
            self._update_expected_delivery()
        return res
     # Warranty from Product
        line.x_studio_p_warranty = (
                line.product_id.product_tmpl_id.x_studio_warranty or ''
            )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._update_expected_delivery()
        return lines

    def write(self, vals):
        res = super().write(vals)

        # Only refresh when product or lead time changes
        if 'customer_lead' in vals or 'product_id' in vals:
            self._update_expected_delivery()

        return res