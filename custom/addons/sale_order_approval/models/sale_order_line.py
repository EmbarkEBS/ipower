from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, vals):
        res = super().write(vals)
        self.mapped("order_id")._evaluate_approval()
        return res

    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.mapped("order_id")._evaluate_approval()
        return lines

    def unlink(self):
        orders = self.mapped("order_id")
        res = super().unlink()
        orders._evaluate_approval()
        return res
