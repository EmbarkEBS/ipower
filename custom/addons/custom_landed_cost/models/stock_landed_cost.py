from odoo import models

class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _get_valuation_lines(self):
        valuation_lines = super()._get_valuation_lines()

        filtered = []

        for line in valuation_lines:
            product = line.product_id

            if not product:
                continue

            exemption = getattr(
                product,
                "x_studio_related_field_8pf_1jn6mtke2",
                False
            )

            # ❌ Exclude 0% products completely from allocation base
            if exemption == "0%":
                continue

            # ✔ Only 5% products remain
            filtered.append(line)

        return filtered
