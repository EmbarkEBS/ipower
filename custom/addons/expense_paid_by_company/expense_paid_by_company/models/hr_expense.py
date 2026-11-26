from odoo import api, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.model
    def default_get(self, fields_list):
        """Default all new expenses to Paid By Company."""

        values = super().default_get(fields_list)

        if "payment_mode" in fields_list:
            values["payment_mode"] = "company_account"

        return values
