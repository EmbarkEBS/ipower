from odoo import models, fields, api


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

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)

        for move in moves:
            if move.move_type != "in_invoice":
                continue

            if not move.invoice_origin:
                continue

            picking = self.env["stock.picking"].search([
                ("name", "=", move.invoice_origin),
                ("picking_type_id.code", "=", "incoming"),
            ], limit=1)

            if picking:
                move.boe_number = picking.boe_number
                move.boe_date = picking.boe_date

        return moves
