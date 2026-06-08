from odoo import models

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_print_custom_invoice(self):
        return self.env.ref(
            "custom_invoice_report.action_report_invoice_custom"
        ).report_action(self)
    def action_preview_custom_invoice(self):
        self.ensure_one()

        report = self.env.ref(
            "custom_invoice_report.action_report_invoice_custom"
        )

        return {
            "type": "ir.actions.act_url",
            "url": "/report/pdf/%s/%s" % (
                report.report_name,
                self.id,
            ),
            "target": "new",
        }