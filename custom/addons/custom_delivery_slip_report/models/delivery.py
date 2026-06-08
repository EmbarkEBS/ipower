from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_print_custom_delivery_slip(self):
        return self.env.ref(
            "custom_delivery_slip_report.action_report_custom_delivery_slip"
        ).report_action(self)
    def action_preview_custom_delivery_slip(self):
        self.ensure_one()

        report = self.env.ref(
            "custom_delivery_slip_report.action_report_custom_delivery_slip"
        )

        return {
            "type": "ir.actions.act_url",
            "url": "/report/pdf/%s/%s" % (
                report.report_name,
                self.id,
            ),
            "target": "new",
        }