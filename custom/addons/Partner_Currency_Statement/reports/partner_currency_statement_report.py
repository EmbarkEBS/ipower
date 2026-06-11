from odoo import models


class PartnerCurrencyStatementReport(models.AbstractModel):
    _name = "report.partner_currency_statement.report_partner_currency_statement"
    _description = "Partner Currency Statement"

    def _get_report_values(self, docids, data=None):

        wizard = self.env[
            "partner.currency.statement.wizard"
        ].browse(docids)

        report_data = wizard._get_report_data()

        return {
            "doc_ids": wizard.ids,
            "doc_model": wizard._name,
            "docs": wizard,
            **report_data,
        }