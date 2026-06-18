from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    boe_number = fields.Char(
        string="BOE Number"
    )

    boe_date = fields.Date(
        string="BOE Date"
    )

    delivery_note = fields.Text(
        string="Delivery Note"
    )

    is_delivery_return = fields.Boolean(
        compute="_compute_is_delivery_return",
        store=False
    )

    @api.depends("move_ids")
    def _compute_is_delivery_return(self):
        for picking in self:
            picking.is_delivery_return = any(
                move.origin_returned_move_id
                for move in picking.move_ids
            )

    def button_validate(self):
        for picking in self:

            if (
                picking.picking_type_id.code == "incoming"
                and not picking.is_delivery_return
            ):
                if not picking.boe_number:
                    raise ValidationError(
                        "BOE Number is required."
                    )

                if not picking.boe_date:
                    raise ValidationError(
                        "BOE Date is required."
                    )

        return super().button_validate()