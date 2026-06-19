from odoo import models, api

class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"


    @api.model
    def _get_default_mail_attachments_widget(self, moves, *args, **kwargs):
        attachments = super()._get_default_mail_attachments_widget(
            moves, *args, **kwargs
        )

        return [
            att for att in attachments
            if att.get("dynamic_report")
        ]

    def _get_mail_params(self, move, mail_template, **kwargs):
        params = super()._get_mail_params(
            move, mail_template, **kwargs
        )

        attachment_ids = params.get("attachment_ids", [])

        attachments = self.env["ir.attachment"].browse(attachment_ids)

        keep_attachments = attachments.filtered(
            lambda a: a.name.startswith("Invoice-")
        )

        params["attachment_ids"] = keep_attachments.ids

        return params

