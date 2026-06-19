from odoo import models, api

class AccountMoveSendWizard(models.TransientModel):
    _inherit = 'account.move.send.wizard'


@api.model
def _get_default_mail_attachments_widget(self, moves, *args, **kwargs):
    attachments = super()._get_default_mail_attachments_widget(
        moves, *args, **kwargs
    )

    if not attachments:
        return attachments

    cleaned_attachments = []

    for attachment in attachments:
        attachment_id = attachment.get("id")
        placeholder = attachment.get("placeholder", False)

        # Remove ONLY Odoo's default invoice PDF attachment
        if attachment_id == "pdf_report" and placeholder:
            continue

        cleaned_attachments.append(attachment)

    return cleaned_attachments
