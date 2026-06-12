from odoo import fields, models


class PartnerCurrencyStatementWizard(models.TransientModel):
    _name = "partner.currency.statement.wizard"
    _description = "Partner Currency Statement Wizard"

    partner_id = fields.Many2one(
        "res.partner",
        required=True
    )

    date_from = fields.Date()

    date_to = fields.Date(
        default=fields.Date.context_today
    )

    def action_print_pdf(self):
        self.ensure_one()

        return self.env.ref(
            "Partner_Currency_Statement.action_partner_currency_statement"
        ).report_action(self)

    def _get_report_data(self):
        self.ensure_one()

        domain = [
            ("partner_id", "=", self.partner_id.id),
            ("parent_state", "=", "posted"),
            (
                "account_id.account_type",
                "in",
                [
                    "asset_receivable",
                    "liability_payable",
                ],
            ),
            "|",
            ("amount_residual_currency", "!=", 0),
            ("amount_residual", "!=", 0),
        ]

        if self.date_from:
            domain.append(
                ("date", ">=", self.date_from)
            )

        if self.date_to:
            domain.append(
                ("date", "<=", self.date_to)
            )

        lines = self.env["account.move.line"].search(
            domain,
            order="date,id"
        )

        currency_summary = {}
        grouped_lines = {}

        for line in lines:

            currency = (
                line.currency_id
                or line.company_currency_id
            )

            currency_key = currency.id

            if currency_key not in currency_summary:
                currency_summary[currency_key] = {
                    "currency": currency,
                    "total": 0.0,
                }

            if currency_key not in grouped_lines:
                grouped_lines[currency_key] = []

            amount = (
                line.amount_residual_currency
                if line.currency_id
                else line.amount_residual
            )

            currency_summary[currency_key]["total"] += amount

            grouped_lines[currency_key].append({
                "date": line.date,
                "document": line.move_id.name,
                "due_date": line.date_maturity,
                "amount": amount,
                "currency": currency.name,
                "move_line": line,
            })

        return {
            "partner": self.partner_id,
            "currency_summary": currency_summary,
            "grouped_lines": grouped_lines,
            "lines": lines,
        }
