from odoo import models

class AccountMoveSend(models.AbstractModel):
 _inherit = "account.move.send"

def _get_default_pdf_report_id(self, move):
    # Disable default invoice PDF generation
    return False

