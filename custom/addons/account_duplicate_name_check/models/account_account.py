from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.constrains("name", "company_id")
    def _check_duplicate_account_name(self):
        for rec in self:
            if not rec.name:
                continue

            normalized_name = " ".join(rec.name.split()).lower()

            duplicate = self.search([
                ("id", "!=", rec.id),
                ("company_id", "=", rec.company_id.id),
            ])

            for account in duplicate:
                existing = " ".join((account.name or "").split()).lower()

                if existing == normalized_name:
                    raise ValidationError(_(
                        'Chart of Account "%s" already exists.'
                    ) % account.name)
