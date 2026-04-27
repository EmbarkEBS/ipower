from odoo import models

class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def compute_landed_cost(self):
        for cost in self:
            for line in cost.cost_lines:

                product = line.product_id

                if product and hasattr(product, "x_studio_exemption"):

                    exemption = product.x_studio_exemption

                    # 0% → remove from computation
                    if exemption == "0%":
                        line.price_unit = 0.0

        return super().compute_landed_cost()
