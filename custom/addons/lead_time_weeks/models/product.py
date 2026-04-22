from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lead_time_weeks = fields.Integer(string="Lead Time (Weeks)")

    def write(self, vals):
        if 'lead_time_weeks' in vals:
            vals['sale_delay'] = vals['lead_time_weeks'] * 7
        return super().write(vals)

    def create(self, vals):
        if vals.get('lead_time_weeks'):
            vals['sale_delay'] = vals['lead_time_weeks'] * 7
        return super().create(vals)