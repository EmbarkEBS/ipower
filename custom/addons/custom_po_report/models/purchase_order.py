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