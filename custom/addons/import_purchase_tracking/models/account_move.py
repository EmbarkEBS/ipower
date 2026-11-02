from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    import_boe_id = fields.Many2one(
        "import.boe", string="Import BOE", copy=False, tracking=True,
        domain="[('company_id', '=', company_id)]", check_company=True,
        help="Bill of Entry covering this vendor bill."
    )
    boe_number = fields.Char(
        string="BOE Number", related="import_boe_id.name", store=True, readonly=True
    )

    @api.constrains("import_boe_id", "company_id", "move_type")
    def _check_import_boe(self):
        for move in self:
            if move.import_boe_id and move.import_boe_id.company_id != move.company_id:
                raise ValidationError(_("The BOE and vendor bill must belong to the same company."))
            if move.import_boe_id and move.move_type not in ("in_invoice", "in_refund"):
                raise ValidationError(_("Import BOE can only be assigned to vendor bills or vendor credit notes."))
