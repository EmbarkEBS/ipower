class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _prepare_valuation_lines(self, forced_quantity=None):

        valuation_lines = super()._prepare_valuation_lines(forced_quantity)

        filtered_lines = []

        for val in valuation_lines:

            cost_line = val.cost_line_id  # IMPORTANT

            if cost_line:

                exemption = getattr(
                    cost_line,
                    "x_studio_related_field_8pf_1jn6mtke2",
                    False
                )

                # ❌ If 0% → remove from allocation base
                if exemption == "0%":
                    continue

            filtered_lines.append(val)

        return filtered_lines
