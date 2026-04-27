from odoo import models

class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _prepare_valuation_lines(self, forced_quantity=None):

        valuation_lines = super()._prepare_valuation_lines(forced_quantity)

        filtered_lines = []

        for line in valuation_lines:

            product = line.product_id

            if product:

                exemption = getattr(
                    product,
                    "x_studio_related_field_8pf_1jn6mtke2",
                    False
                )

                # ❌ exclude 0% products BEFORE compute happens
                if exemption == "0%":
                    continue

            filtered_lines.append(line)

        return filtered_lines
