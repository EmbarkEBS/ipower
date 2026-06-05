from odoo import models

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_print_custom_vendor_bill(self):
        return self.env.ref(
            "custom_vendor_bill_report.action_report_vendor_bill"
        ).report_action(self)