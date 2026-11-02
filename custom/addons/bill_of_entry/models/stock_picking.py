from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    bill_of_entry_id = fields.Many2one(
        "bill.of.entry",
        string="Bill of Entry",
        check_company=True,
        domain="[('company_id', '=', company_id)]",
    )

    boe_number = fields.Char(
        related="bill_of_entry_id.boe_number",
        string="BOE Number",
        readonly=True,
    )

    boe_date = fields.Date(
        related="bill_of_entry_id.boe_date",
        string="BOE Date",
        readonly=True,
    )