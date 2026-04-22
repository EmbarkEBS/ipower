from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lead_time_weeks = fields.Float(
        string="Customer Lead Time (Weeks)",
        compute="_compute_weeks",
        inverse="_inverse_weeks",
        store=True
    )

    def _compute_weeks(self):
        for rec in self:
            sale_delay = getattr(rec, 'sale_delay', 0.0)
            rec.lead_time_weeks = sale_delay / 7.0 if sale_delay else 0.0

    def _inverse_weeks(self):
        for rec in self:
            if hasattr(rec, 'sale_delay'):
                rec.sale_delay = rec.lead_time_weeks * 7.0