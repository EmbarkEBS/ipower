from odoo import models

class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def button_validate(self):
        for cost in self:

            for val in cost.valuation_adjustment_lines:

                product = val.product_id 

                if product:

                    exemption = product.x_studio_exemption

                    # 0% → remove landed cost impact
                    if exemption == "0%":
                        val.additional_landed_cost = 0

        return super().button_validate()
