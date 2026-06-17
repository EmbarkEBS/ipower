from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_quotation_send(self):
        action = super().action_quotation_send()
        report = self.env.ref(
            "custom_sale_report.action_report_saleorder_custom",
            raise_if_not_found=False,
        )
        if report:
            action.setdefault("context", {})
            action["context"].update({
                "default_report_template_ids": [(6, 0, [report.id])]
            })
        return action
