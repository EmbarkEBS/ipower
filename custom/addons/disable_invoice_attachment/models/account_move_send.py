from odoo import models, api

class AccountMoveSendWizard(models.TransientModel):
    _inherit = 'account.move.send.wizard'


    @api.model
    def _get_default_mail_attachments_widget(self, moves, *args, **kwargs):
        attachments = super()._get_default_mail_attachments_widget(
            moves, *args, **kwargs
        )

        filtered_attachments = []

        for attachment in attachments:
            name = attachment.get("name", "")

            # Remove standard invoice PDF
            if name.endswith(".pdf") and not name.startswith("Invoice-"):
                continue

            filtered_attachments.append(attachment)

        return filtered_attachments
