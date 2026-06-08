from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_print_custom_so(self):
        return self.env.ref(
            "custom_sale_report.action_report_custom_sale_order"
        ).report_action(self)

    @api.onchange('partner_id')
    def _onchange_partner_incoterm(self):
        if self.partner_id.x_studio_incoterm:
            self.incoterm = self.partner_id.x_studio_incoterm.id

    def action_preview_custom_sale_order(self):
        self.ensure_one()

        report = self.env.ref(
            "custom_sale_report.action_report_custom_sale_order"
        )

        return {
            "type": "ir.actions.act_url",
            "url": "/report/pdf/%s/%s" % (
                report.report_name,
                self.id,
            ),
            "target": "new",
        }