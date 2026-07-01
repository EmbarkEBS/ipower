from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Creation Date
    editable_create_date = fields.Datetime(
        string="Creation Date",
        compute="_compute_editable_dates",
        inverse="_inverse_create_date",
    )

    # Confirmation Date
    editable_confirmation_date = fields.Datetime(
        string="Confirmation Date",
        compute="_compute_editable_dates",
        inverse="_inverse_confirmation_date",
    )

    def _compute_editable_dates(self):
        for rec in self:
            rec.editable_create_date = rec.create_date
            rec.editable_confirmation_date = rec.date_approve

    def _inverse_create_date(self):
        for rec in self:
         if rec.editable_create_date:
            self.env.cr.execute("""
                UPDATE purchase_order
                SET create_date = %s
                WHERE id = %s
            """, (
                rec.editable_create_date,
                rec.id,
            ))

    def _inverse_confirmation_date(self):
        for rec in self:
         value = rec.editable_confirmation_date or None

        self.env.cr.execute("""
            UPDATE purchase_order
            SET date_approve = %s
            WHERE id = %s
        """, (
            value,
            rec.id,
        ))