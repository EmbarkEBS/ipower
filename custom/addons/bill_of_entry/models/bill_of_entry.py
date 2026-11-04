from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from markupsafe import Markup, escape


class BillOfEntry(models.Model):
    _name = "bill.of.entry"
    _description = "Bill of Entry"
    _order = "id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        default="New",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )

    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order",
        required=True,
        check_company=True,
        domain="[('company_id', '=', company_id)]",
    )

    boe_number = fields.Char(
        string="BOE Number",
        compute="_compute_boe_details",
        readonly=True,
    )

    boe_date = fields.Date(
        string="BOE Date",
        compute="_compute_boe_details",
        readonly=True,
    )

    vendor_bill_ids = fields.Many2many(
        "account.move",
        string="Vendor Bills",
        compute="_compute_vendor_bill_ids",
        readonly=True,
    )

    additional_bill_line_ids = fields.One2many(
        "bill.of.entry.additional.line",
        "bill_of_entry_id",
        string="Additional Bill Invoice Lines",
    )
    # additional_account_summary_ids = fields.One2many(
    #     "bill.of.entry.account.summary",
    #     "bill_of_entry_id",
    #     string="Account Allocation Summary",
    #     readonly=True,
    # )

    additional_account_summary_html = fields.Html(
        string="Account Allocation Summary",
        compute="_compute_additional_account_summary_html",
        readonly=True,
    )
    
    account_wise_allocated_summary = fields.Char(
        string="Account-wise Allocated Amount",
        compute="_compute_account_wise_allocated_summary",
    )

    notes = fields.Text(string="Notes")

    @api.depends(
        "additional_bill_line_ids.account_id",
        "additional_bill_line_ids.currency_id",
        "additional_bill_line_ids.allocated_amount",
    )
    def _compute_account_wise_allocated_summary(self):
        for record in self:
            totals = {}
    
            for line in record.additional_bill_line_ids:
                if not line.account_id or not line.currency_id:
                    continue
    
                key = (line.account_id.id, line.currency_id.id)
    
                if key not in totals:
                    totals[key] = {
                        "account": line.account_id.display_name,
                        "currency": line.currency_id,
                        "amount": 0.0,
                    }
    
                totals[key]["amount"] += line.allocated_amount
    
            summary = []
    
            for item in totals.values():
                currency = item["currency"]
                amount = currency.round(item["amount"])
    
                formatted_amount = f"{amount:,.2f}"
    
                if currency.position == "before":
                    formatted_amount = f"{currency.symbol} {formatted_amount}"
                else:
                    formatted_amount = f"{formatted_amount} {currency.symbol}"
    
                summary.append(
                    f"{item['account']}: {formatted_amount}"
                )
    
            record.account_wise_allocated_summary = " | ".join(summary)

    @api.depends(
        "additional_bill_line_ids.account_id",
        "additional_bill_line_ids.currency_id",
        "additional_bill_line_ids.allocated_amount",
    )
    def _compute_additional_account_summary_html(self):
        for record in self:
            totals = {}
    
            for line in record.additional_bill_line_ids:
                if not line.account_id or not line.currency_id:
                    continue
    
                key = (line.account_id.id, line.currency_id.id)
    
                if key not in totals:
                    totals[key] = {
                        "account": line.account_id.display_name,
                        "currency": line.currency_id,
                        "amount": 0.0,
                    }
    
                totals[key]["amount"] += line.allocated_amount
    
            rows = []
    
            for item in sorted(
                totals.values(),
                key=lambda value: value["account"],
            ):
                currency = item["currency"]
                amount = currency.round(item["amount"])
                formatted_amount = f"{amount:,.2f}"
    
                if currency.position == "before":
                    formatted_amount = f"{currency.symbol} {formatted_amount}"
                else:
                    formatted_amount = f"{formatted_amount} {currency.symbol}"
    
                rows.append(
                    Markup(
                        "<tr><td>{}</td><td class='text-end'>{}</td></tr>"
                    ).format(
                        escape(item["account"]),
                        escape(formatted_amount),
                    )
                )
    
            if rows:
                record.additional_account_summary_html = Markup(
                    """
                    <table class="table table-sm table-bordered">
                        <thead>
                            <tr>
                                <th>Account</th>
                                <th class="text-end">Total Allocated Amount</th>
                            </tr>
                        </thead>
                        <tbody>{}</tbody>
                    </table>
                    """
                ).format(Markup("").join(rows))
            else:
                record.additional_account_summary_html = Markup(
                    "<p>No account allocations available.</p>"
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("bill.of.entry")
                    or "New"
                )
        return super().create(vals_list)

    @api.depends("purchase_order_id")
    def _compute_boe_details(self):
        Picking = self.env["stock.picking"]

        for record in self:
            record.boe_number = False
            record.boe_date = False

            if not record.purchase_order_id:
                continue

            receipts = Picking.search(
                [
                    ("purchase_id", "=", record.purchase_order_id.id),
                    ("picking_type_id.code", "=", "incoming"),
                    "|",
                    ("boe_number", "!=", False),
                    ("boe_date", "!=", False),
                ],
                order="date_done desc, scheduled_date desc, id desc",
                limit=1,
            )

            if receipts:
                record.boe_number = receipts.boe_number
                record.boe_date = receipts.boe_date

    @api.depends("purchase_order_id")
    def _compute_vendor_bill_ids(self):
        Move = self.env["account.move"]

        for record in self:
            if not record.purchase_order_id:
                record.vendor_bill_ids = Move
                continue

            bills = Move.search(
                [
                    ("move_type", "=", "in_invoice"),
                    ("state", "=", "posted"),
                    ("company_id", "=", record.company_id.id),
                    (
                        "invoice_line_ids.purchase_line_id.order_id",
                        "=",
                        record.purchase_order_id.id,
                    ),
                ]
            )

            record.vendor_bill_ids = bills


class BillOfEntryAdditionalLine(models.Model):
    _name = "bill.of.entry.additional.line"
    _description = "Bill of Entry Additional Invoice Line"

    bill_of_entry_id = fields.Many2one(
        "bill.of.entry",
        string="Bill of Entry",
        required=True,
        ondelete="cascade",
    )

    company_id = fields.Many2one(
        related="bill_of_entry_id.company_id",
        store=True,
        readonly=True,
    )

    invoice_line_id = fields.Many2one(
        "account.move.line",
        string="Vendor Bill Invoice Line",
        required=True,
        check_company=True,
        domain=[
            ("move_id.move_type", "=", "in_invoice"),
            ("move_id.state", "=", "posted"),
            ("display_type", "=", "product"),
        ],
    )

    move_id = fields.Many2one(
        "account.move",
        string="Vendor Bill",
        related="invoice_line_id.move_id",
        readonly=True,
    )

    vendor_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        related="move_id.partner_id",
        readonly=True,
    )

    invoice_date = fields.Date(
        string="Invoice Date",
        related="move_id.invoice_date",
        readonly=True,
    )

    invoice_line_name = fields.Char(
        string="Invoice Line",
        related="invoice_line_id.name",
        readonly=True,
    )

    quantity = fields.Float(
        string="Quantity",
        related="invoice_line_id.quantity",
        readonly=True,
    )

    price_unit = fields.Float(
        string="Unit Price",
        related="invoice_line_id.price_unit",
        readonly=True,
    )

    subtotal = fields.Monetary(
        string="Subtotal",
        related="invoice_line_id.price_subtotal",
        currency_field="currency_id",
        readonly=True,
        store=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="invoice_line_id.currency_id",
        readonly=True,
        store=True,
    )

    account_id = fields.Many2one(
        "account.account",
        string="Account",
        related="invoice_line_id.account_id",
        readonly=True,
        store=True,
    )

    percentage = fields.Float(
        string="Percentage",
        default=100.0,
    )

    allocated_amount = fields.Monetary(
        string="Allocated Amount",
        compute="_compute_allocated_amount",
        currency_field="currency_id",
        store=True,
    )

    @api.depends("subtotal", "percentage")
    def _compute_allocated_amount(self):
        for line in self:
            line.allocated_amount = (
                line.subtotal * line.percentage / 100.0
            )

    @api.constrains("invoice_line_id")
    def _check_invoice_line(self):
        for line in self:
            invoice_line = line.invoice_line_id

            if not invoice_line:
                continue

            bill = invoice_line.move_id

            if bill.move_type != "in_invoice" or bill.state != "posted":
                raise ValidationError(
                    _("Only invoice lines from posted vendor bills are allowed.")
                )

            if bill.company_id != line.bill_of_entry_id.company_id:
                raise ValidationError(
                    _("The vendor bill and Bill of Entry must belong to the same company.")
                )

    @api.constrains("percentage")
    def _check_percentage(self):
        for line in self:
            if line.percentage < 0 or line.percentage > 100:
                raise ValidationError(
                    _("Percentage must be between 0 and 100.")
                )

class BillOfEntryAccountSummary(models.Model):
    _name = "bill.of.entry.account.summary"
    _description = "Bill of Entry Account Allocation Summary"
    _auto = False
    _order = "account_id"

    bill_of_entry_id = fields.Many2one(
        "bill.of.entry",
        string="Bill of Entry",
        readonly=True,
    )

    account_id = fields.Many2one(
        "account.account",
        string="Account",
        readonly=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        readonly=True,
    )

    allocated_amount = fields.Monetary(
        string="Total Allocated Amount",
        currency_field="currency_id",
        readonly=True,
    )

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW bill_of_entry_account_summary AS (
                SELECT
                    MIN(line.id) AS id,
                    line.bill_of_entry_id,
                    line.account_id,
                    line.currency_id,
                    SUM(line.allocated_amount) AS allocated_amount
                FROM bill_of_entry_additional_line line
                WHERE line.account_id IS NOT NULL
                GROUP BY
                    line.bill_of_entry_id,
                    line.account_id,
                    line.currency_id
            )
        """)
