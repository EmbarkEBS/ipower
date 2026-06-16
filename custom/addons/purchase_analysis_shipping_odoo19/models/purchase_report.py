# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.tools.sql import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    x_studio_weightkg_1 = fields.Char(
        string="Weight (KG)",
        readonly=True,
    )

    x_studio_dimensions_1 = fields.Char(
        string="Dimensions",
        readonly=True,
    )

    x_studio_pickup_address = fields.Char(
        string="Pickup Address",
        readonly=True,
    )

    x_studio_delivery_location = fields.Char(
        string="Delivery Location",
        readonly=True,
    )

    def _select(self):
        return SQL(
            "%s, "
            "po.x_studio_weightkg_1 AS x_studio_weightkg_1, "
            "po.x_studio_dimensions_1 AS x_studio_dimensions_1, "
            "po.x_studio_pickup_address AS x_studio_pickup_address, "
            "po.x_studio_delivery_location AS x_studio_delivery_location",
            super()._select(),
        )

    def _group_by(self):
        return SQL(
            "%s, "
            "po.x_studio_weightkg_1, "
            "po.x_studio_dimensions_1, "
            "po.x_studio_pickup_address, "
            "po.x_studio_delivery_location",
            super()._group_by(),
        )