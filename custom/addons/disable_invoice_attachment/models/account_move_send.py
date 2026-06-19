import logging
from odoo import models

_logger = logging.getLogger(__name__)

class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    def __getattribute__(self, name):
        if "pdf" in name.lower() or "report" in name.lower():
            _logger.warning("METHOD AVAILABLE: %s", name)
        return super().__getattribute__(name)