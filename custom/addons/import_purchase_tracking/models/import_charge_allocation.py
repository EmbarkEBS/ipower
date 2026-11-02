from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class ImportChargeAllocation(models.Model):
    _name = "import.charge.allocation"
    _description = "Import Charge Allocation"
    _order = "date desc, id desc"
    _check_company_auto = True

    name = fields.Char(compute="_compute_name", store=True)
    boe_id = fields.Many2one(
        "import.boe", string="BOE", required=True, ondelete="cascade",
        domain="[('company_id', '=', company_id)]", check_company=True, index=True
    )
    company_id = fields.Many2one(related="boe_id.company_id", store=True, readonly=True)
    date = fields.Date(related="move_line_id.date", store=True, readonly=True)
    move_line_id = fields.Many2one(
        "account.move.line", string="Vendor Bill Expense Line", required=True,
        domain="[('move_id.move_type', 'in', ('in_invoice', 'in_refund')), "
               "('move_id.state', '!=', 'cancel')]",
        check_company=True, ondelete="restrict", index=True
    )
    move_id = fields.Many2one(related="move_line_id.move_id", string="Vendor Bill", store=True, readonly=True)
    bill_number = fields.Char(related="move_id.name", string="Bill Number", store=True)
    bill_supplier_id = fields.Many2one(
        related="move_id.partner_id", string="Bill Supplier", store=True, readonly=True
    )
    account_id = fields.Many2one(related="move_line_id.account_id", string="Expense Account", store=True)
    purchase_order_id = fields.Many2one(
        "purchase.order", string="Purchase Order", required=True,
        domain="[('company_id', '=', company_id)]", check_company=True, index=True
    )
    po_supplier_id = fields.Many2one(
        related="purchase_order_id.partner_id", string="PO Supplier", store=True, readonly=True
    )
    charge_type = fields.Selection([
        ("boe_duty", "BOE / Duty Bill"),
        ("customs_duty", "Customs Duty"),
        ("clearing", "Clearing Charge"),
        ("freight", "Freight Charge"),
        ("other", "Other Import Charge"),
    ], required=True, string="Charge Type", default="customs_duty")
    amount = fields.Monetary(
        string="Allocated Amount (Company Currency)", required=True,
        currency_field="company_currency_id"
    )
    company_currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", store=True, readonly=True
    )
    move_line_balance = fields.Monetary(
        related="move_line_id.balance", string="Bill Line Balance",
        currency_field="company_currency_id", readonly=True
    )
    state = fields.Selection(related="move_id.state", string="Bill Status", store=True)

    @api.depends("move_id.name", "purchase_order_id.name", "charge_type")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s - %s" % (
                rec.move_id.name or _("New"),
                rec.purchase_order_id.name or _("No PO"),
                dict(self._fields["charge_type"].selection).get(rec.charge_type, ""),
            )

    @api.constrains("boe_id", "move_line_id", "purchase_order_id", "amount", "charge_type")
    def _check_allocation(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("Allocated amount must be greater than zero."))
            move = rec.move_line_id.move_id
            if move.import_boe_id != rec.boe_id:
                raise ValidationError(_("The vendor bill must have the same Import BOE as this allocation."))
            if move.company_id != rec.boe_id.company_id:
                raise ValidationError(_("The BOE, bill and PO must belong to the same company."))
            if rec.purchase_order_id.company_id != rec.boe_id.company_id:
                raise ValidationError(_("The PO must belong to the same company as the BOE."))
            linked_pos = rec.boe_id.purchase_order_line_ids.mapped("purchase_order_id")
            if rec.purchase_order_id not in linked_pos:
                raise ValidationError(_("First add this Purchase Order to the BOE's Purchase Orders tab."))
            if move.state == "cancel":
                raise ValidationError(_("You cannot allocate a cancelled vendor bill."))
            if rec.move_line_id.display_type != "product":
                raise ValidationError(_("Select an expense/product line, not a section, note, tax or payable line."))
            if rec.move_line_id.account_id.account_type not in ("expense", "expense_direct_cost"):
                raise ValidationError(_("Select a vendor bill line posted to an expense account."))
            total = sum(self.search([
                ("id", "!=", rec.id),
                ("move_line_id", "=", rec.move_line_id.id),
            ]).mapped("amount")) + rec.amount
            available = abs(rec.move_line_id.balance)
            if float_compare(total, available, precision_rounding=rec.company_currency_id.rounding) > 0:
                raise ValidationError(_(
                    "Total allocations for this bill line (%(allocated)s) cannot exceed its company-currency balance (%(available)s).",
                    allocated=total, available=available
                ))

    @api.onchange("move_line_id")
    def _onchange_move_line_id(self):
        for rec in self:
            if rec.move_line_id:
                rec.boe_id = rec.move_line_id.move_id.import_boe_id
                if rec.move_line_id.purchase_line_id:
                    rec.purchase_order_id = rec.move_line_id.purchase_line_id.order_id
                rec.amount = abs(rec.move_line_id.balance)
