# from odoo import models


# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     def write(self, vals):
#         res = super().write(vals)
#         self.mapped("order_id")._evaluate_approval()
#         return res

#     def create(self, vals_list):
#         lines = super().create(vals_list)
#         lines.mapped("order_id")._evaluate_approval()
#         return lines

#     def unlink(self):
#         orders = self.mapped("order_id")
#         res = super().unlink()
#         orders._evaluate_approval()
#         return res

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):

        lines = super().create(
            vals_list
        )

        # Do not evaluate while quotation
        # duplication is in progress.
        if not self.env.context.get(
            "skip_sale_approval"
        ):
            lines.mapped(
                "order_id"
            )._evaluate_approval()

        return lines

    # --------------------------------------------------
    # WRITE
    # --------------------------------------------------
    def write(self, vals):

        res = super().write(vals)

        # Do not evaluate while duplication
        # is in progress.
        if not self.env.context.get(
            "skip_sale_approval"
        ):
            self.mapped(
                "order_id"
            )._evaluate_approval()

        return res

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------
    def unlink(self):

        orders = self.mapped(
            "order_id"
        )

        res = super().unlink()

        # Recalculate approval after deleting
        # quotation lines.
        if not self.env.context.get(
            "skip_sale_approval"
        ):
            orders._evaluate_approval()

        return res
