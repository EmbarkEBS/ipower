from odoo import models, api

class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"


    @api.model
    def _get_default_mail_attachments_widget(self, moves, *args, **kwargs):
            attachments = super()._get_default_mail_attachments_widget(
                moves, *args, **kwargs
            )

            # Keep only dynamic reports (your custom report)
            return [
                att
                for att in attachments
                if att.get("dynamic_report")
            ]

