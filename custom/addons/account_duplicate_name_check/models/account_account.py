import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning("######## CUSTOM CREATE EXECUTED ########")
        return super().create(vals_list)

    def write(self, vals):
        _logger.warning("######## CUSTOM WRITE EXECUTED ########")
        return super().write(vals)
