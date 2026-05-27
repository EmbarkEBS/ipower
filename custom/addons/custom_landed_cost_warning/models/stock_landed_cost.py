from odoo import models, fields, api, _


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    is_working = fields.Boolean(
        string="Is Working",
        default=True
    )

    @api.onchange('picking_ids', 'account_move_id')
    def _onchange_duplicate_landed_cost_warning(self):

        message = ""

        # =====================================
        # CHECK TRANSFERS
        # =====================================
        for picking in self.picking_ids:

            if not picking._origin.id:
                continue

            existing_lc = self.env['stock.landed.cost'].search([
                ('picking_ids', 'in', [picking._origin.id])
            ], limit=1)

            if existing_lc:

                message += _(
                    "Transfer %s already used in Landed Cost %s\n\n"
                ) % (
                    picking.name,
                    existing_lc.name
                )

        # =====================================
        # CHECK VENDOR BILL
        # =====================================
        if self.account_move_id and self.account_move_id._origin.id:

            existing_bill_lc = self.env['stock.landed.cost'].search([
                ('account_move_id', '=', self.account_move_id._origin.id)
            ], limit=1)

            if existing_bill_lc:

                message += _(
                    "Vendor Bill %s already used in Landed Cost %s"
                ) % (
                    self.account_move_id.name,
                    existing_bill_lc.name
                )

        # =====================================
        # SHOW WARNING
        # =====================================
        if message:

            return {
                'warning': {
                    'title': _('Warning'),
                    'message': message,
                }
            }
