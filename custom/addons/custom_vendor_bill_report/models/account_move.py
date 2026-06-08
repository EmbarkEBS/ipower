from odoo import models

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_preview_custom_vendor_bill(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_url",
            "url": "/report/html/custom_vendor_bill_report.vendor_bill_template/%s" % self.id,
            "target": "new",
        }