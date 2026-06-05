from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_print_custom_delivery_slip(self):
        return self.env.ref(
            "custom_delivery_slip_report.action_report_custom_delivery_slip"
        ).report_action(self)