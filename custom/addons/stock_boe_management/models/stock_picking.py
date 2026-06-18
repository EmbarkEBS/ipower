from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    boe_number = fields.Char(string="BOE Number")
    boe_date = fields.Date(string="BOE Date")
    delivery_note = fields.Text(string="Delivery Note")

    is_delivery_return = fields.Boolean(
        compute="_compute_flags"
    )

    is_normal_receipt = fields.Boolean(
        compute="_compute_flags"
    )

    @api.depends(
        "picking_type_id.code",
        "move_ids.origin_returned_move_id"
    )
    def _compute_flags(self):
        for picking in self:
            is_return = any(
                move.origin_returned_move_id
                for move in picking.move_ids
            )

            picking.is_delivery_return = is_return

            picking.is_normal_receipt = (
                picking.picking_type_id.code == "incoming"
                and not is_return
            )

    def button_validate(self):
        for picking in self:
            if picking.is_normal_receipt:
                if not picking.boe_number:
                    raise ValidationError("BOE Number is required.")

                if not picking.boe_date:
                    raise ValidationError("BOE Date is required.")

        return super().button_validate()
