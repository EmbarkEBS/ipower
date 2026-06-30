from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    editable_create_date = fields.Datetime(
        string="Creation Date",
        compute="_compute_editable_create_date",
        inverse="_inverse_editable_create_date",
    )

    def _compute_editable_create_date(self):
        for rec in self:
            rec.editable_create_date = rec.create_date

    def _inverse_editable_create_date(self):
        for rec in self:
            if rec.editable_create_date:
                self.env.cr.execute("""
                    UPDATE sale_order
                    SET create_date = %s
                    WHERE id = %s
                """, (
                    rec.editable_create_date,
                    rec.id,
                ))