from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.mapped("order_id")._evaluate_approval()
        return lines

    def write(self, vals):
        res = super().write(vals)
        self.mapped("order_id")._evaluate_approval()
        return res

    def unlink(self):
        orders = self.mapped("order_id")
        res = super().unlink()
        orders._evaluate_approval()
        return res
