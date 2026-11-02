from odoo import api, fields, models, Command, _
from odoo.exceptions import ValidationError


class BillOfEntry(models.Model):
    _name = "bill.of.entry"
    _description = "Bill of Entry"
    _order = "boe_date desc, id desc"
    _check_company_auto = True

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        copy=False,
        default="New",
    )

    boe_number = fields.Char(
        string="BOE Number",
        required=True,
    )

    boe_date = fields.Date(
        string="BOE Date",
        required=True,
        default=fields.Date.context_today,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Currency",
        readonly=True,
    )

    purchase_order_ids = fields.Many2many(
        "purchase.order",
        "bill_of_entry_purchase_order_rel",
        "boe_id",
        "purchase_order_id",
        string="Purchase Orders",
        check_company=True,
    )

    vendor_ids = fields.Many2many(
        "res.partner",
        string="Vendors",
        compute="_compute_vendor_ids",
    )

    vendor_bill_line_ids = fields.One2many(
        "bill.of.entry.line",
        "boe_id",
        string="Vendor Bills",
        domain=[("line_type", "=", "vendor")],
    )

    additional_bill_line_ids = fields.One2many(
        "bill.of.entry.line",
        "boe_id",
        string="Additional Bills",
        domain=[("line_type", "=", "additional")],
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
    )

    notes = fields.Text(string="Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("bill.of.entry")
                    or "New"
                )
        return super().create(vals_list)

    @api.depends("purchase_order_ids", "purchase_order_ids.partner_id")
    def _compute_vendor_ids(self):
        for record in self:
            record.vendor_ids = record.purchase_order_ids.mapped(
                "partner_id"
            )

    @api.onchange("purchase_order_ids")
    def _onchange_purchase_order_ids(self):
        """Refresh the Vendor Bills tab from the selected POs."""
        for record in self:
            # Remove only automatically populated vendor-tab lines.
            existing_lines = record.vendor_bill_line_ids
            commands = [
                Command.delete(line.id)
                for line in existing_lines
                if line.id
            ]
            commands += [
                Command.clear()
            ] if existing_lines and not any(
                line.id for line in existing_lines
            ) else []

            # Find posted vendor bills whose invoice lines link to
            # any of the selected purchase orders.
            po_ids = record.purchase_order_ids.ids
            if not po_ids:
                record.vendor_bill_line_ids = commands
                continue

            bills = self.env["account.move"].search([
                ("move_type", "=", "in_invoice"),
                ("state", "=", "posted"),
                ("company_id", "=", record.company_id.id),
                ("invoice_line_ids.purchase_line_id.order_id", "in", po_ids),
            ])

            for bill in bills:
                commands.append(Command.create({
                    "move_id": bill.id,
                    "line_type": "vendor",
                    "percentage": 100.0,
                }))

            record.vendor_bill_line_ids = commands

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    @api.constrains("purchase_order_ids", "company_id")
    def _check_po_company(self):
        for record in self:
            if any(
                po.company_id != record.company_id
                for po in record.purchase_order_ids
            ):
                raise ValidationError(_(
                    "All purchase orders must belong to the BOE company."
                ))


class BillOfEntryLine(models.Model):
    _name = "bill.of.entry.line"
    _description = "Bill of Entry Bill Line"
    _order = "sequence, id"
    _check_company_auto = True

    sequence = fields.Integer(default=10)

    boe_id = fields.Many2one(
        "bill.of.entry",
        string="Bill of Entry",
        required=True,
        ondelete="cascade",
        check_company=True,
    )

    company_id = fields.Many2one(
        related="boe_id.company_id",
        store=True,
        readonly=True,
    )

    line_type = fields.Selection(
        [
            ("vendor", "Vendor Bill"),
            ("additional", "Additional Bill"),
        ],
        required=True,
        default="vendor",
    )

    move_id = fields.Many2one(
        "account.move",
        string="Vendor Bill",
        required=True,
        check_company=True,
        domain=[
            ("move_type", "=", "in_invoice"),
            ("state", "=", "posted"),
        ],
    )

    vendor_id = fields.Many2one(
        related="move_id.partner_id",
        string="Supplier",
        readonly=True,
    )

    bill_number = fields.Char(
        related="move_id.ref",
        string="Bill Reference",
        readonly=True,
    )

    bill_date = fields.Date(
        related="move_id.invoice_date",
        string="Bill Date",
        readonly=True,
    )

    currency_id = fields.Many2one(
        related="move_id.currency_id",
        string="Bill Currency",
        readonly=True,
    )

    bill_amount = fields.Monetary(
        related="move_id.amount_total",
        currency_field="currency_id",
        string="Bill Amount",
        readonly=True,
    )

    # Used for Additional Bills; not displayed in Vendor Bills.
    percentage = fields.Float(
        string="Percentage (%)",
        default=100.0,
        digits=(16, 4),
    )

    allocated_amount = fields.Monetary(
        string="Allocated Amount",
        currency_field="currency_id",
        compute="_compute_allocated_amount",
        store=True,
    )

    account_id = fields.Many2one(
        "account.account",
        string="Chart of Accounts",
        check_company=True,
        domain="[('company_ids', 'in', [company_id])]",
    )

    description = fields.Char(string="Description")

    @api.depends("bill_amount", "percentage")
    def _compute_allocated_amount(self):
        for line in self:
            line.allocated_amount = (
                (line.bill_amount or 0.0)
                * (line.percentage or 0.0)
                / 100.0
            )

    @api.constrains("percentage", "line_type")
    def _check_percentage(self):
        for line in self:
            if line.line_type == "additional" and not (
                0 <= line.percentage <= 100
            ):
                raise ValidationError(_(
                    "Additional bill percentage must be between 0 and 100."
                ))

    @api.constrains("move_id", "boe_id", "line_type")
    def _check_bill(self):
        for line in self:
            bill = line.move_id
            boe = line.boe_id

            if bill.state != "posted" or bill.move_type != "in_invoice":
                raise ValidationError(_(
                    "Only posted vendor bills can be selected."
                ))

            if bill.company_id != boe.company_id:
                raise ValidationError(_(
                    "The vendor bill and BOE must belong to the same company."
                ))

            if line.line_type == "vendor":
                selected_po_ids = set(boe.purchase_order_ids.ids)
                bill_po_ids = set(
                    bill.invoice_line_ids
                    .mapped("purchase_line_id.order_id").ids
                )
                if selected_po_ids and not (
                    selected_po_ids & bill_po_ids
                ):
                    raise ValidationError(_(
                        "This vendor bill is not linked to a selected "
                        "purchase order."
                    ))
