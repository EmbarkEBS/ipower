import logging
from odoo import models

_logger = logging.getLogger(**name**)

class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"


def _get_mail_params(self, move, mail_template, **kwargs):
    params = super()._get_mail_params(move, mail_template, **kwargs)

    _logger.warning("MAIL PARAMS: %s", params)

    return params

