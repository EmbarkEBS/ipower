from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    picking_ids = fields.Many2many(
        "stock.picking",
        string="Transfers"
    )

    @api.constrains("picking_ids", "state")
    def _check_duplicate_landed_cost(self):
        for rec in self:
            if not rec.picking_ids:
                continue

            existing = self.search([
                ("id", "!=", rec.id),
                ("state", "!=", "cancel"),
                ("picking_ids", "in", rec.picking_ids.ids),
            ], limit=1)

            if existing:
                raise ValidationError(_(
                    "Landed Cost already exists for transfer(s):\n%s\n\nExisting LC: %s"
                ) % (
                    ", ".join(rec.picking_ids.mapped("name")),
                    existing.name
                ))