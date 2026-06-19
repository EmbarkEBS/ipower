import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"

    @api.model
    def _get_default_mail_attachments_widget(self, moves, *args, **kwargs):
        attachments = super()._get_default_mail_attachments_widget(
            moves, *args, **kwargs
        )

        _logger.warning("=== ATTACHMENTS START ===")
        for att in attachments:
            _logger.warning("%s", att)
        _logger.warning("=== ATTACHMENTS END ===")

        return attachments