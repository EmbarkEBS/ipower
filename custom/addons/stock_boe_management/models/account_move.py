from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    boe_number = fields.Char(
        string="BOE Number",
        compute="_compute_boe_fields",
        readonly=True,
        store=True,
    )

    boe_date = fields.Date(
        string="BOE Date",
        compute="_compute_boe_fields",
        readonly=True,
        store=True,
    )

    @api.depends(
        "invoice_line_ids.purchase_line_id.order_id"
    )
    def _compute_boe_fields(self):
        for move in self:
            move.boe_number = False
            move.boe_date = False

            purchase_orders = move.invoice_line_ids.mapped(
                "purchase_line_id.order_id"
            )

            if not purchase_orders:
                continue

            receipt = self.env["stock.picking"].search([
                ("purchase_id", "in", purchase_orders.ids),
                ("picking_type_id.code", "=", "incoming"),
                ("state", "=", "done"),
            ], order="id desc", limit=1)

            if receipt:
                move.boe_number = receipt.boe_number
                move.boe_date = receipt.boe_date
