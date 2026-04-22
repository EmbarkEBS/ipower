from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    lead_time_weeks = fields.Float(
        string="Customer Lead Time (Weeks)",
        compute="_compute_lead_time_weeks",
        inverse="_inverse_lead_time_weeks",
        store=True
    )

    @api.depends('sale_delay')
    def _compute_lead_time_weeks(self):
        for rec in self:
            rec.lead_time_weeks = rec.sale_delay / 7.0 if rec.sale_delay else 0.0

    def _inverse_lead_time_weeks(self):
        for rec in self:
            rec.sale_delay = rec.lead_time_weeks * 7.0 if rec.lead_time_weeks else 0.0