from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_print_payment_receipt(self):
        self.ensure_one()

        return self.env.ref(
            "custom_payment_receipt_report.action_payment_receipt"
        ).report_action(self)