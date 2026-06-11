from odoo import models

class ReportPartnerCurrencyStatement(models.AbstractModel):
    _name = "report.partner_currency_statement.statement_report"
    _description = "Partner Currency Statement Report"

    def _get_report_values(self, docids, data=None):
        wizard = self.env["partner.currency.statement.wizard"].browse(docids)

        report_data = wizard._get_report_data()

        return {
            "doc_ids": wizard.ids,
            "doc_model": wizard._name,
            "docs": wizard,
            **report_data,
        }
