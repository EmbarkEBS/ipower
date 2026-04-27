from odoo import models

class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _get_valuation_lines(self):
        valuation_lines = super()._get_valuation_lines()

        for cost in self:
            for line in cost.cost_lines:

                # Only Custom Duty line (better: use boolean field instead of name)
                if line.product_id.name == "Custom Duty":

                    exemption = line.product_id.product_tmpl_id.x_studio_related_field_8pf_1jn6mtke2

                    # CASE 0% → remove landed cost impact
                    if exemption == "0%":
                        for val in valuation_lines:
                            if val.cost_line_id == line:
                                val.additional_landed_cost = 0

        return valuation_lines