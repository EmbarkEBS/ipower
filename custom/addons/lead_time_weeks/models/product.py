from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lead_time_weeks = fields.Float(
        string="Customer Lead Time (Weeks)",
        compute="_compute_lead_time_weeks",
        inverse="_inverse_lead_time_weeks",
        store=True
    )

    @api.depends_context('uid')  # safe trigger
    def _compute_lead_time_weeks(self):
        for rec in self:
            # safe access (avoid crash if field missing)
            sale_delay = getattr(rec, 'sale_delay', 0.0)
            rec.lead_time_weeks = sale_delay / 7.0 if sale_delay else 0.0

    def _inverse_lead_time_weeks(self):
        for rec in self:
            if hasattr(rec, 'sale_delay'):
                rec.sale_delay = rec.lead_time_weeks * 7.0 if rec.lead_time_weeks else 0.0