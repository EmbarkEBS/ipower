from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lead_time_weeks = fields.Float(
        string="Customer Lead Time (Weeks)",
        compute="_compute_weeks",
        inverse="_inverse_weeks",
        store=True
    )

    @api.depends('sale_delay')
    def _compute_weeks(self):
        for rec in self:
            rec.lead_time_weeks = rec.sale_delay / 7 if rec.sale_delay else 0.0

    def _inverse_weeks(self):
        for rec in self:
            rec.sale_delay = rec.lead_time_weeks * 7 if rec.lead_time_weeks else 0.0