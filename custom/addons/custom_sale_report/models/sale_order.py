from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contact_person_id = fields.Many2one(
        'res.partner',
        string='Attention'
    )

    def action_print_custom_so(self):
        return self.env.ref(
            "custom_sale_report.action_report_custom_sale_order"
        ).report_action(self)

    @api.onchange('partner_id')
    def _onchange_partner_id_custom(self):

        # Incoterm
        if self.partner_id and self.partner_id.x_studio_incoterm:
            self.incoterm = self.partner_id.x_studio_incoterm.id

        # Clear Attention when customer changes
        self.contact_person_id = False

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