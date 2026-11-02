from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ImportBoe(models.Model):
    _name = "import.boe"
    _description = "Bill of Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "boe_date desc, name desc"
    _check_company_auto = True

    name = fields.Char(string="BOE Number", required=True, tracking=True, index=True)
    boe_date = fields.Date(string="BOE Date", tracking=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True,
        default=lambda self: self.env.company, index=True
    )
    purchase_order_line_ids = fields.One2many(
        "import.boe.po.line", "boe_id", string="Purchase Orders"
    )
    allocation_ids = fields.One2many(
        "import.charge.allocation", "boe_id", string="Charge Allocations"
    )
    vendor_bill_ids = fields.One2many(
        "account.move", "import_boe_id", string="Vendor Bills"
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", store=True, readonly=True
    )
    customs_duty_total = fields.Monetary(
        compute="_compute_totals", string="Customs Duty", currency_field="currency_id", store=False
    )
    clearing_total = fields.Monetary(
        compute="_compute_totals", string="Clearing Charges", currency_field="currency_id", store=False
    )
    freight_total = fields.Monetary(
        compute="_compute_totals", string="Freight Charges", currency_field="currency_id", store=False
    )
    boe_duty_total = fields.Monetary(
        compute="_compute_totals", string="BOE / Duty Bill", currency_field="currency_id", store=False
    )
    other_total = fields.Monetary(
        compute="_compute_totals", string="Other Charges", currency_field="currency_id", store=False
    )
    total_import_charges = fields.Monetary(
        compute="_compute_totals", string="Total Import Charges", currency_field="currency_id", store=False
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("boe_name_company_unique", "unique(name, company_id)", "This BOE number already exists for this company."),
    ]

    @api.depends(
        "allocation_ids.amount", "allocation_ids.charge_type",
        "allocation_ids.move_line_id.move_id.state",
        "allocation_ids.move_line_id.move_id.move_type",
    )
    def _compute_totals(self):
        for boe in self:
            totals = {
                "boe_duty": 0.0, "customs": 0.0, "clearing": 0.0,
                "freight": 0.0, "other": 0.0,
            }
            for allocation in boe.allocation_ids:
                move = allocation.move_line_id.move_id
                if move.state != "posted" or move.move_type not in ("in_invoice", "in_refund"):
                    continue
                sign = -1.0 if move.move_type == "in_refund" else 1.0
                totals_key = {
                    "boe_duty": "boe_duty",
                    "customs_duty": "customs",
                    "clearing": "clearing",
                    "freight": "freight",
                    "other": "other",
                }[allocation.charge_type]
                totals[totals_key] += sign * allocation.amount
            boe.boe_duty_total = totals["boe_duty"]
            boe.customs_duty_total = totals["customs"]
            boe.clearing_total = totals["clearing"]
            boe.freight_total = totals["freight"]
            boe.other_total = totals["other"]
            boe.total_import_charges = sum(totals.values())


class ImportBoePoLine(models.Model):
    _name = "import.boe.po.line"
    _description = "BOE Purchase Order Link"
    _rec_name = "purchase_order_id"
    _order = "id"

    boe_id = fields.Many2one("import.boe", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="boe_id.company_id", store=True, readonly=True)
    purchase_order_id = fields.Many2one(
        "purchase.order", string="Purchase Order", required=True,
        domain="[('company_id', '=', company_id)]", check_company=True
    )
    partner_id = fields.Many2one(
        "res.partner", string="PO Supplier",
        related="purchase_order_id.partner_id", store=True, readonly=True
    )
    date_order = fields.Datetime(related="purchase_order_id.date_order", string="PO Date", store=True)
    currency_id = fields.Many2one(related="boe_id.currency_id", store=True, readonly=True)

    _sql_constraints = [
        ("boe_po_unique", "unique(boe_id, purchase_order_id)", "This PO is already linked to this BOE."),
    ]

    @api.constrains("boe_id", "purchase_order_id")
    def _check_company_match(self):
        for rec in self:
            if rec.purchase_order_id and rec.purchase_order_id.company_id != rec.boe_id.company_id:
                raise ValidationError(_("The PO and BOE must belong to the same company."))
