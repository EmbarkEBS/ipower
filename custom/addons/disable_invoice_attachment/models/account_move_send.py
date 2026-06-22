from odoo import models

class AccountMoveSend(models.AbstractModel):
 _inherit = "account.move.send"

def _get_default_pdf_report_id(self, move):
    return self.env.ref(
        "custom_invoice_report.invoice_template",
        raise_if_not_found=False,
    )

