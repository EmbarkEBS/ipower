from odoo import models, api

class AccountMoveSendWizard(models.TransientModel):
    _inherit = 'account.move.send.wizard'

    @api.model
    def _get_default_mail_attachments_widget(self, moves, *args, **kwargs):
        """
        Intercepts and filters out ONLY the native system-generated invoice PDF 
        while preserving your custom reports defined in the email template.
        """
        # Safely fetch native dictionary values with framework parameters
        attachments = super(AccountMoveSendWizard, self)._get_default_mail_attachments_widget(moves, *args, **kwargs)
        
        if not attachments:
            return []

        cleaned_attachments = []
        for attachment in attachments:
            # Check if this is the default core framework invoice pdf report
            is_pdf = attachment.get('mimetype') == 'application/pdf'
            is_core_report = attachment.get('placeholder') is True or attachment.get('id') == 'pdf_report'
            
            # Drop only the core system-generated pdf; pass everything else (your custom template report)
            if is_pdf and is_core_report:
                continue
                
            cleaned_attachments.append(attachment)
            
        return cleaned_attachments
