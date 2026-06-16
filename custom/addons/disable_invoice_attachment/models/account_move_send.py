from odoo import models, api

class AccountMoveSendWizard(models.TransientModel):
    _inherit = 'account.move.send.wizard'

    @api.model
    def _get_default_mail_attachments_widget(self, moves, mail_template=None):
        """
        Intercepts and filters out the automatic invoice PDF attachment.
        """
        # Call the core Odoo logic to fetch the native array of values
        attachments = super(AccountMoveSendWizard, self)._get_default_mail_attachments_widget(moves, mail_template=mail_template)
        
        # Filter list to bypass any element containing standard PDF mime structures
        cleaned_attachments = []
        for attachment in attachments:
            if attachment.get('mimetype') == 'application/pdf':
                continue
            cleaned_attachments.append(attachment)
            
        return cleaned_attachments
