from odoo import models, api


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        if not res.get("product_id"):
            product = self.env["product.product"].search(
                [('can_be_expensed', '=', True)],
                limit=1
            )
            if product:
                res["product_id"] = product.id

        return res
