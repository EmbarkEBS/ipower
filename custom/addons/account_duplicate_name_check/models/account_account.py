from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = "account.account"

    def _check_duplicate_account_name(self, name):
        if not name:
            return

        normalized_name = " ".join(name.split()).lower()

        accounts = self.search([
            ("id", "not in", self.ids),
            ("company_id", "=", self.company_id.id if self.company_id else self.env.company.id),
        ])

        for account in accounts:
            existing = " ".join((account.name or "").split()).lower()
            if existing == normalized_name:
                raise ValidationError(_(
                    'Chart of Account "%s" already exists.\n'
                    'Please use a different account name.'
                ) % account.name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company = self.env["res.company"].browse(
                vals.get("company_id", self.env.company.id)
            )

            temp = self.with_company(company).new(vals)
            temp._check_duplicate_account_name(vals.get("name"))

        return super().create(vals_list)

    def write(self, vals):
        result = super().write(vals)

        if "name" in vals:
            for rec in self:
                rec._check_duplicate_account_name(rec.name)

        return result