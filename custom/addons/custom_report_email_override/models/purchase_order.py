from odoo import models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_rfq_send(self):
        action = super().action_rfq_send()
        report = self.env.ref(
            "custom_po_report.action_report_purchase_order_custom",
            raise_if_not_found=False,
        )
        if report:
            action.setdefault("context", {})
            action["context"].update({
                "default_report_template_ids": [(6, 0, [report.id])]
            })
        return action
