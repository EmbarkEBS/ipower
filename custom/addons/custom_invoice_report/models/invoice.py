from odoo import models

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_print_custom_invoice(self):
        return self.env.ref(
            "custom_invoice_report.action_report_invoice_custom"
        ).report_action(self)