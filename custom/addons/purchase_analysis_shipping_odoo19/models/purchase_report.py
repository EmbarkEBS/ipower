from odoo import fields, models

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    x_studio_weightkg_1 = fields.Char(readonly=True)
    x_studio_dimensions_1 = fields.Char(readonly=True)
    x_studio_pickup_address = fields.Char(readonly=True)
    x_studio_delivery_location = fields.Char(readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res.update({
            'x_studio_weightkg_1': 'po.x_studio_weightkg_1',
            'x_studio_dimensions_1': 'po.x_studio_dimensions_1',
            'x_studio_pickup_address': 'po.x_studio_pickup_address',
            'x_studio_delivery_location': 'po.x_studio_delivery_location',
        })
        return res
