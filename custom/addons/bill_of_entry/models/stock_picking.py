from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    boe_number = fields.Char(
        string="BOE Number",
        copy=False,
    )

    boe_date = fields.Date(
        string="BOE Date",
        copy=False,
    )