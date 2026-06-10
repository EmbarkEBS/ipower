from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    def action_print_custom_po(self):
        return self.env.ref(
            'custom_po_report.action_report_custom_purchase_order'
        ).report_action(self)

    @api.onchange('partner_id')
    def _onchange_partner_incoterm(self):
        if self.partner_id.x_studio_incoterm:
            self.incoterm_id = self.partner_id.x_studio_incoterm.id
    def action_preview_custom_po(self):
        self.ensure_one()

        report = self.env.ref(
            "custom_po_report.action_report_custom_purchase_order"
        )

        return {
            "type": "ir.actions.act_url",
            "url": "/report/pdf/%s/%s" % (
                report.report_name,
                self.id,
            ),
            "target": "new",
        }
    @api.onchange('partner_id')
    def _onchange_partner_id_contact(self):
        self.x_studio_contact_person = False

        if not self.partner_id:
            return {
                'domain': {
                    'x_studio_contact_person': [('id', '=', 0)]
                }
            }

        return {
            'domain': {
                'x_studio_contact_person': [
                    ('parent_id', '=', self.partner_id.id),
                    ('is_company', '=', False),
                ]
            }
        }