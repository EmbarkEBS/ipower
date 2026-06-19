import logging
from odoo import models, api

_logger = logging.getLogger(name)

class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"


@api.model
def _get_default_mail_attachments_widget(self, moves, *args, **kwargs):
    attachments = super()._get_default_mail_attachments_widget(
        moves, *args, **kwargs
    )

    for att in attachments:
        _logger.warning("WIZARD ATTACHMENT => %s", att)

    return [
        att for att in attachments
        if att.get("dynamic_report")
    ]

def _generate_dynamic_reports(self, invoices_data):
    _logger.warning("GENERATE DYNAMIC REPORTS")
    return super()._generate_dynamic_reports(invoices_data)

