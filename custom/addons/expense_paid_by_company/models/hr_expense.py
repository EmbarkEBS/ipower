from odoo import api, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.model
    def default_get(self, fields_list):
        """Set Paid By to Company when creating a new expense."""
        values = super().default_get(fields_list)

        if "payment_mode" in fields_list:
            values["payment_mode"] = "company_account"

        return values

    @api.onchange("employee_id")
    def _onchange_employee_id_paid_by_company(self):
        """
        When an employee is selected, automatically set Paid By
        to Company when the employee configuration allows company payment.
        """
        for expense in self:
            if expense.employee_id:
                if expense.employee_id.expense_paid_by_company:
                    expense.payment_mode = "company_account"