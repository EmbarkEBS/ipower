from odoo import models

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_preview_custom_vendor_bill(self):
        self.ensure_one()

        report = self.env.ref(
            "custom_vendor_bill_report.action_vendor_bill_report"
        )

        return {
            "type": "ir.actions.act_url",
            "url": "/report/html/%s/%s" % (
                report.report_name,
                self.id,
            ),
            "target": "new",
        }