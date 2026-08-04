from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = "account.account"

    def _validate_duplicate_name(self, name, company_ids):
        if not name:
            return

        normalized = " ".join(name.split()).lower()

        company_ids = company_ids or [self.env.company.id]

        accounts = self.search([
            ("company_ids", "in", company_ids),
            ("id", "not in", self.ids),
        ])

        for account in accounts:
            existing = " ".join((account.name or "").split()).lower()
            if existing == normalized:
                raise ValidationError(_(
                    'The Chart of Account "%s" already exists.'
                ) % account.name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_ids = vals.get("company_ids")
            if company_ids:
                # Extract IDs from M2M commands
                ids = []
                for command in company_ids:
                    if command[0] == 6:
                        ids.extend(command[2])
                    elif command[0] == 4:
                        ids.append(command[1])
            else:
                ids = [self.env.company.id]

            self._validate_duplicate_name(vals.get("name"), ids)

        return super().create(vals_list)

    def write(self, vals):
        for rec in self:
            if "company_ids" in vals:
                ids = []
                for command in vals["company_ids"]:
                    if command[0] == 6:
                        ids.extend(command[2])
                    elif command[0] == 4:
                        ids.append(command[1])
            else:
                ids = rec.company_ids.ids

            self._validate_duplicate_name(
                vals.get("name", rec.name),
                ids,
            )

        return super().write(vals)
