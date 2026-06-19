from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    boe_number = fields.Char(
        string="BOE Number",
        copy=False,
    )

    boe_date = fields.Date(
        string="BOE Date",
        copy=False,
    )
