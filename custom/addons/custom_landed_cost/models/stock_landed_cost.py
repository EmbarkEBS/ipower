from odoo import models

class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _compute_landed_cost(self):
        # Call standard Odoo logic first
        res = super()._compute_landed_cost()

        for cost in self:
            for line in cost.cost_lines:

                # Only Custom Duty line
                if line.product_id.name == "Custom Duty":

                    exemption = line.product_id.product_tmpl_id.x_studio_exemption

                    # CASE 1: 0% → remove cost completely
                    if exemption == "0%":
                        line.price_unit = 0

                        # Optional: also reset allocations
                        for adj in cost.valuation_adjustment_lines:
                            if adj.cost_line_id == line:
                                adj.additional_landed_cost = 0

                    # CASE 2: 5% → keep normal behavior
                    elif exemption == "5%":
                        pass

        return res