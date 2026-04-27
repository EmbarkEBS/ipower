from odoo import models

class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _compute_landed_cost(self):

        res = super()._compute_landed_cost()

        for cost in self:
            for line in cost.cost_lines:

                exemption = getattr(
                    line,
                    "x_studio_related_field_8pf_1jn6mtke2",
                    False
                )

                # Only apply logic for Custom Duty type lines if needed
                if exemption == "0%":

                    # Remove impact from valuation lines
                    for val_line in cost.valuation_adjustment_lines:
                        if val_line.cost_line_id == line:
                            val_line.additional_landed_cost = 0

            # 🔥 VERY IMPORTANT → recompute totals
            total = sum(cost.valuation_adjustment_lines.mapped('additional_landed_cost'))

            if total != cost.amount_total:
                # push remaining amount to eligible lines
                valid_lines = cost.valuation_adjustment_lines.filtered(
                    lambda v: getattr(
                        v.cost_line_id,
                        "x_studio_related_field_8pf_1jn6mtke2",
                        False
                    ) != "0%"
                )

                if valid_lines:
                    per_line = cost.amount_total / len(valid_lines)
                    for v in valid_lines:
                        v.additional_landed_cost = per_line

        return res
