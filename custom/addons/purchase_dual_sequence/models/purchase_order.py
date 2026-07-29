# from odoo import api, fields, models


# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'

#     is_rfq = fields.Boolean(default=True)

#     @api.model_create_multi
#     def create(self, vals_list):

#         for vals in vals_list:
#             if vals.get('name', 'New') == 'New':
#                 vals['name'] = self.env['ir.sequence'].next_by_code(
#                     'purchase.rfq'
#                 ) or 'New'

#         return super().create(vals_list)

#     def button_confirm(self):

#         for order in self:
#             if order.is_rfq:
#                 order.name = self.env['ir.sequence'].next_by_code(
#                     'purchase.order.custom'
#                 )
#                 order.is_rfq = False

#         return super().button_confirm()
from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_rfq = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            company = self.env['res.company'].browse(
                vals.get('company_id', self.env.company.id)
            )

            if vals.get('auto_generated'):
                vals['name'] = self.env['ir.sequence'].with_company(
                    company
                ).next_by_code('purchase.rfq') or 'New'

            elif vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].with_company(
                    company
                ).next_by_code('purchase.rfq') or 'New'

        return super().create(vals_list)

    def button_confirm(self):

        for order in self:
            if order.is_rfq:

                order.name = self.env['ir.sequence'].with_company(
                    order.company_id
                ).next_by_code('purchase.order.custom')

                order.is_rfq = False

        return super().button_confirm()