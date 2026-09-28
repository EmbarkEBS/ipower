from odoo import fields, models, tools


class InvoiceMarginReport(models.Model):
    _name = "invoice.margin.report"
    _description = "Invoice Margin Analysis"
    _auto = False
    _rec_name = "invoice_number"
    _order = "invoice_date desc, invoice_number desc, id"

    # =========================================================================
    # BASIC INVOICE INFORMATION
    # =========================================================================

    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        readonly=True,
    )

    invoice_number = fields.Char(
        string="Invoice Number",
        readonly=True,
    )

    invoice_date = fields.Date(
        string="Invoice Date",
        readonly=True,
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        readonly=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        readonly=True,
    )

    # =========================================================================
    # SALES ORDER / PRODUCT
    # =========================================================================

    sale_order_number = fields.Char(
        string="SO Number",
        readonly=True,
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        readonly=True,
    )

    quantity = fields.Float(
        string="Quantity",
        readonly=True,
        aggregator="sum",
    )

    selling_price = fields.Monetary(
        string="Selling Price",
        currency_field="currency_id",
        readonly=True,
        aggregator="avg",
    )

    # =========================================================================
    # REVENUE
    # =========================================================================

    revenue_amount = fields.Monetary(
        string="Revenue",
        currency_field="currency_id",
        readonly=True,
        aggregator="sum",
    )

    # =========================================================================
    # COGS
    #
    # IMPORTANT:
    # These are now SQL VIEW fields.
    # They are NOT Python computed fields.
    # Therefore Odoo Pivot can aggregate them.
    # =========================================================================

    cogs = fields.Monetary(
        string="COGS",
        currency_field="currency_id",
        readonly=True,
        aggregator="sum",
    )

    # =========================================================================
    # LINE MARGIN
    # =========================================================================

    line_margin_amount = fields.Monetary(
        string="Line Margin",
        currency_field="currency_id",
        readonly=True,
        aggregator="sum",
    )

    line_margin_percentage = fields.Float(
        string="Line Margin %",
        readonly=True,
        aggregator="avg",
    )

    # =========================================================================
    # INVOICE TOTALS
    #
    # These are retained for the normal report view.
    # Do NOT use these as Product-level pivot measures because they are
    # invoice-level values repeated on every invoice line.
    # =========================================================================

    total_revenue = fields.Monetary(
        string="Total Revenue",
        currency_field="currency_id",
        readonly=True,
        aggregator="sum",
    )

    total_cogs = fields.Monetary(
        string="Total COGS",
        currency_field="currency_id",
        readonly=True,
        aggregator="sum",
    )

    total_margin_amount = fields.Monetary(
        string="Total Margin",
        currency_field="currency_id",
        readonly=True,
        aggregator="sum",
    )

    total_margin_percentage = fields.Float(
        string="Total Margin %",
        readonly=True,
        aggregator="avg",
    )

    # =========================================================================
    # SQL VIEW
    # =========================================================================

    def init(self):

        tools.drop_view_if_exists(
            self.env.cr,
            self._table,
        )

        self.env.cr.execute(
            """
            CREATE VIEW invoice_margin_report AS (

                WITH cogs_per_line AS (

                    /*
                     * Odoo 19 creates two COGS lines for each eligible
                     * customer invoice line:
                     *
                     *   1. Stock valuation line
                     *   2. Expense / COGS line
                     *
                     * For an outgoing invoice:
                     *
                     *   Expense / COGS = positive balance
                     *   Stock valuation = negative balance
                     *
                     * Therefore we take the positive COGS balance.
                     *
                     * cogs_origin_id points back to the invoice line.
                     */

                    SELECT
                        cogs_line.cogs_origin_id AS invoice_line_id,

                        SUM(
                            CASE
                                WHEN cogs_line.balance > 0
                                THEN cogs_line.balance
                                ELSE 0
                            END
                        ) AS cogs_company_amount

                    FROM account_move_line cogs_line

                    JOIN account_move cogs_move
                        ON cogs_move.id = cogs_line.move_id

                    WHERE
                        cogs_line.display_type = 'cogs'
                        AND cogs_move.state = 'posted'
                        AND cogs_move.move_type = 'out_invoice'
                        AND cogs_line.cogs_origin_id IS NOT NULL

                    GROUP BY
                        cogs_line.cogs_origin_id
                ),

                invoice_line_base AS (

                    SELECT

                        aml.id AS id,

                        am.id AS invoice_id,

                        am.name AS invoice_number,

                        am.invoice_date AS invoice_date,

                        am.partner_id AS customer_id,

                        am.company_id AS company_id,

                        am.currency_id AS currency_id,

                        aml.product_id AS product_id,

                        aml.quantity AS quantity,

                        aml.price_unit AS selling_price,

                        aml.price_subtotal AS revenue_amount,

                        COALESCE(
                            cogs.cogs_company_amount,
                            0.0
                        ) AS cogs_company_amount,

                        /*
                         * Company currency rate.
                         *
                         * Odoo currency rates are relative rates.
                         */

                        COALESCE(
                            (
                                SELECT r.rate
                                FROM res_currency_rate r
                                WHERE
                                    r.currency_id = company_currency.id
                                    AND r.name <= COALESCE(
                                        am.invoice_date,
                                        am.date
                                    )
                                    AND (
                                        r.company_id = am.company_id
                                        OR r.company_id IS NULL
                                    )
                                ORDER BY
                                    CASE
                                        WHEN r.company_id = am.company_id
                                        THEN 0
                                        ELSE 1
                                    END,
                                    r.name DESC,
                                    r.id DESC
                                LIMIT 1
                            ),
                            1.0
                        ) AS company_currency_rate,

                        /*
                         * Invoice currency rate.
                         */

                        COALESCE(
                            (
                                SELECT r.rate
                                FROM res_currency_rate r
                                WHERE
                                    r.currency_id = am.currency_id
                                    AND r.name <= COALESCE(
                                        am.invoice_date,
                                        am.date
                                    )
                                    AND (
                                        r.company_id = am.company_id
                                        OR r.company_id IS NULL
                                    )
                                ORDER BY
                                    CASE
                                        WHEN r.company_id = am.company_id
                                        THEN 0
                                        ELSE 1
                                    END,
                                    r.name DESC,
                                    r.id DESC
                                LIMIT 1
                            ),
                            1.0
                        ) AS invoice_currency_rate,

                        /*
                         * Sales Order number.
                         */

                        (
                            SELECT STRING_AGG(
                                DISTINCT so.name,
                                ', '
                                ORDER BY so.name
                            )
                            FROM sale_order_line sol

                            JOIN sale_order so
                                ON so.id = sol.order_id

                            JOIN sale_order_line_invoice_rel rel
                                ON rel.order_line_id = sol.id

                            WHERE
                                rel.invoice_line_id = aml.id
                        ) AS sale_order_number

                    FROM account_move_line aml

                    JOIN account_move am
                        ON am.id = aml.move_id

                    JOIN res_company company
                        ON company.id = am.company_id

                    JOIN res_currency company_currency
                        ON company_currency.id = company.currency_id

                    LEFT JOIN cogs_per_line cogs
                        ON cogs.invoice_line_id = aml.id

                    WHERE

                        am.move_type = 'out_invoice'

                        AND am.state = 'posted'

                        AND aml.display_type = 'product'

                        AND aml.product_id IS NOT NULL
                )

                SELECT

                    base.id,

                    base.invoice_id,

                    base.invoice_number,

                    base.invoice_date,

                    base.customer_id,

                    base.company_id,

                    base.currency_id,

                    base.sale_order_number,

                    base.product_id,

                    base.quantity,

                    base.selling_price,

                    base.revenue_amount,

                    /*
                     * Convert actual accounting COGS from company currency
                     * into the invoice currency.
                     *
                     * Conversion:
                     *
                     * company amount
                     * × company currency rate
                     * ÷ invoice currency rate
                     */

                    (
                        base.cogs_company_amount
                        * base.company_currency_rate
                        / NULLIF(
                            base.invoice_currency_rate,
                            0
                        )
                    ) AS cogs,

                    /*
                     * Line margin.
                     */

                    (
                        base.revenue_amount
                        -
                        (
                            base.cogs_company_amount
                            * base.company_currency_rate
                            / NULLIF(
                                base.invoice_currency_rate,
                                0
                            )
                        )
                    ) AS line_margin_amount,

                    /*
                     * Line margin percentage.
                     */

                    CASE

                        WHEN base.revenue_amount <> 0

                        THEN (

                            (
                                base.revenue_amount
                                -
                                (
                                    base.cogs_company_amount
                                    * base.company_currency_rate
                                    / NULLIF(
                                        base.invoice_currency_rate,
                                        0
                                    )
                                )
                            )
                            / base.revenue_amount

                        ) * 100.0

                        ELSE 0.0

                    END AS line_margin_percentage,

                    /*
                     * Invoice total revenue.
                     *
                     * This is intentionally retained for the normal
                     * invoice-level report.
                     */

                    SUM(base.revenue_amount)
                        OVER (
                            PARTITION BY base.invoice_id
                        ) AS total_revenue,

                    /*
                     * Invoice total COGS.
                     */

                    SUM(
                        (
                            base.cogs_company_amount
                            * base.company_currency_rate
                            / NULLIF(
                                base.invoice_currency_rate,
                                0
                            )
                        )
                    )
                    OVER (
                        PARTITION BY base.invoice_id
                    ) AS total_cogs,

                    /*
                     * Invoice total margin.
                     */

                    (
                        SUM(base.revenue_amount)
                            OVER (
                                PARTITION BY base.invoice_id
                            )
                        -
                        SUM(
                            (
                                base.cogs_company_amount
                                * base.company_currency_rate
                                / NULLIF(
                                    base.invoice_currency_rate,
                                    0
                                )
                            )
                        )
                        OVER (
                            PARTITION BY base.invoice_id
                        )
                    ) AS total_margin_amount,

                    /*
                     * Invoice total margin percentage.
                     */

                    CASE

                        WHEN
                            SUM(base.revenue_amount)
                                OVER (
                                    PARTITION BY base.invoice_id
                                ) <> 0

                        THEN (

                            (
                                SUM(base.revenue_amount)
                                    OVER (
                                        PARTITION BY base.invoice_id
                                    )
                                -
                                SUM(
                                    (
                                        base.cogs_company_amount
                                        * base.company_currency_rate
                                        / NULLIF(
                                            base.invoice_currency_rate,
                                            0
                                        )
                                    )
                                )
                                OVER (
                                    PARTITION BY base.invoice_id
                                )
                            )
                            /
                            SUM(base.revenue_amount)
                                OVER (
                                    PARTITION BY base.invoice_id
                                )

                        ) * 100.0

                        ELSE 0.0

                    END AS total_margin_percentage

                FROM invoice_line_base base

            )
            """
        )

# from collections import defaultdict

# from odoo import api, fields, models, tools


# class InvoiceMarginReport(models.Model):
#     _name = "invoice.margin.report"
#     _description = "Invoice Margin Analysis"
#     _auto = False
#     _rec_name = "invoice_number"
#     _order = "invoice_date desc, invoice_number desc, id"

#     # -------------------------------------------------------------------------
#     # BASIC INVOICE INFORMATION
#     # -------------------------------------------------------------------------

#     invoice_id = fields.Many2one(
#         "account.move",
#         string="Invoice",
#         readonly=True,
#     )

#     invoice_number = fields.Char(
#         string="Invoice Number",
#         readonly=True,
#     )

#     invoice_date = fields.Date(
#         string="Invoice Date",
#         readonly=True,
#     )

#     customer_id = fields.Many2one(
#         "res.partner",
#         string="Customer",
#         readonly=True,
#     )

#     company_id = fields.Many2one(
#         "res.company",
#         string="Company",
#         readonly=True,
#     )

#     currency_id = fields.Many2one(
#         "res.currency",
#         string="Currency",
#         readonly=True,
#     )

#     # -------------------------------------------------------------------------
#     # SALES ORDER / PRODUCT
#     # -------------------------------------------------------------------------

#     sale_order_number = fields.Char(
#         string="SO Number",
#         readonly=True,
#     )

#     product_id = fields.Many2one(
#         "product.product",
#         string="Product",
#         readonly=True,
#     )

#     quantity = fields.Float(
#         string="Quantity",
#         readonly=True,
#     )

#     selling_price = fields.Monetary(
#         string="Selling Price",
#         currency_field="currency_id",
#         readonly=True,
#     )

#     # -------------------------------------------------------------------------
#     # REVENUE
#     # -------------------------------------------------------------------------

#     revenue_amount = fields.Monetary(
#         string="Revenue",
#         currency_field="currency_id",
#         readonly=True,
#     )

#     # -------------------------------------------------------------------------
#     # COGS / MARGIN
#     # -------------------------------------------------------------------------

#     cogs = fields.Monetary(
#         string="COGS",
#         currency_field="currency_id",
#         compute="_compute_margin_values",
#         readonly=True,
#     )

#     line_margin_amount = fields.Monetary(
#         string="Line Margin",
#         currency_field="currency_id",
#         compute="_compute_margin_values",
#         readonly=True,
#     )

#     line_margin_percentage = fields.Float(
#         string="Line Margin %",
#         compute="_compute_margin_values",
#         readonly=True,
#     )

#     # -------------------------------------------------------------------------
#     # INVOICE TOTALS
#     # -------------------------------------------------------------------------

#     total_revenue = fields.Monetary(
#         string="Total Revenue",
#         currency_field="currency_id",
#         readonly=True,
#     )

#     total_cogs = fields.Monetary(
#         string="Total COGS",
#         currency_field="currency_id",
#         compute="_compute_margin_values",
#         readonly=True,
#     )

#     total_margin_amount = fields.Monetary(
#         string="Total Margin",
#         currency_field="currency_id",
#         compute="_compute_margin_values",
#         readonly=True,
#     )

#     total_margin_percentage = fields.Float(
#         string="Total Margin %",
#         compute="_compute_margin_values",
#         readonly=True,
#     )

#     # -------------------------------------------------------------------------
#     # COGS HELPER
#     # -------------------------------------------------------------------------

#     def _get_cogs_company_amounts(self, invoice_lines):
#         """
#         Return actual posted Accounting COGS amounts in company currency.

#         Odoo 19 creates two COGS accounting lines for a real-time valued
#         outgoing invoice:

#             1. Stock valuation account
#             2. Expense / COGS account

#         Both lines have:
#             display_type = 'cogs'
#             cogs_origin_id = invoice product line

#         We intentionally take the EXPENSE / COGS account line.

#         This is the actual accounting COA COGS amount.
#         It is NOT standard_price.
#         """

#         result = defaultdict(float)

#         if not invoice_lines:
#             return result

#         # Only real invoice product lines are relevant.
#         invoice_lines = invoice_lines.filtered(
#             lambda line:
#             line.display_type == "product"
#             and line.move_id.state == "posted"
#             and line.move_id.move_type == "out_invoice"
#         )

#         if not invoice_lines:
#             return result

#         AccountMoveLine = self.env["account.move.line"]

#         # Build the expected COGS/expense account for each invoice line.
#         line_expense_accounts = {}

#         for invoice_line in invoice_lines:
#             product = invoice_line.product_id

#             if not product:
#                 continue

#             product = product.with_company(invoice_line.company_id)

#             accounts = product.product_tmpl_id.get_product_accounts(
#                 fiscal_pos=invoice_line.move_id.fiscal_position_id
#             )

#             expense_account = (
#                 accounts.get("expense")
#                 or invoice_line.move_id.journal_id.default_account_id
#             )

#             if expense_account:
#                 line_expense_accounts[invoice_line.id] = expense_account.id

#         if not line_expense_accounts:
#             return result

#         # Search all posted COGS accounting lines belonging to these
#         # invoice product lines.
#         cogs_lines = AccountMoveLine.search([
#             ("display_type", "=", "cogs"),
#             ("move_id.state", "=", "posted"),
#             ("move_id.move_type", "=", "out_invoice"),
#             ("cogs_origin_id", "in", list(line_expense_accounts.keys())),
#         ])

#         for cogs_line in cogs_lines:
#             origin_line = cogs_line.cogs_origin_id

#             if not origin_line:
#                 continue

#             expected_expense_account = line_expense_accounts.get(
#                 origin_line.id
#             )

#             if not expected_expense_account:
#                 continue

#             # IMPORTANT:
#             # Only take the expense / COGS account line.
#             #
#             # Do NOT take the stock valuation account line.
#             if cogs_line.account_id.id != expected_expense_account:
#                 continue

#             # balance is already in company currency.
#             #
#             # For a normal outgoing invoice:
#             # COGS expense line = debit / positive balance.
#             #
#             # Therefore we use the positive accounting balance.
#             result[origin_line.id] += cogs_line.balance

#         return result

#     # -------------------------------------------------------------------------
#     # COMPUTED MARGIN VALUES
#     # -------------------------------------------------------------------------

#     @api.depends(
#         "invoice_id",
#         "revenue_amount",
#         "currency_id",
#         "company_id",
#     )
#     def _compute_margin_values(self):

#         # Group report rows by invoice.
#         invoice_rows = defaultdict(list)

#         for record in self:
#             if record.invoice_id:
#                 invoice_rows[record.invoice_id.id].append(record)

#         if not invoice_rows:
#             return

#         # Get all invoice product lines required for all invoices.
#         invoice_ids = list(invoice_rows.keys())

#         invoices = self.env["account.move"].browse(invoice_ids).exists()

#         all_invoice_lines = invoices.mapped("invoice_line_ids").filtered(
#             lambda line:
#             line.display_type == "product"
#             and line.move_id.state == "posted"
#             and line.move_id.move_type == "out_invoice"
#         )

#         # Get actual Accounting COGS in company currency.
#         cogs_company_amounts = self._get_cogs_company_amounts(
#             all_invoice_lines
#         )

#         # ---------------------------------------------------------------------
#         # Prepare invoice total COGS
#         # ---------------------------------------------------------------------

#         invoice_total_cogs_company = defaultdict(float)

#         for invoice_line in all_invoice_lines:
#             invoice_total_cogs_company[
#                 invoice_line.move_id.id
#             ] += cogs_company_amounts.get(invoice_line.id, 0.0)

#         # ---------------------------------------------------------------------
#         # Compute each report row
#         # ---------------------------------------------------------------------

#         for record in self:

#             invoice = record.invoice_id

#             if not invoice:
#                 record.cogs = 0.0
#                 record.line_margin_amount = 0.0
#                 record.line_margin_percentage = 0.0
#                 record.total_cogs = 0.0
#                 record.total_margin_amount = 0.0
#                 record.total_margin_percentage = 0.0
#                 continue

#             invoice_currency = invoice.currency_id
#             company = invoice.company_id

#             conversion_date = (
#                 invoice.invoice_date
#                 or invoice.date
#                 or fields.Date.context_today(invoice)
#             )

#             # -------------------------------------------------------------
#             # Find original invoice line
#             # -------------------------------------------------------------

#             invoice_line = self.env["account.move.line"].browse(
#                 record.id
#             ).exists()

#             if not invoice_line:
#                 record.cogs = 0.0
#                 record.line_margin_amount = 0.0
#                 record.line_margin_percentage = 0.0
#                 record.total_cogs = 0.0
#                 record.total_margin_amount = 0.0
#                 record.total_margin_percentage = 0.0
#                 continue

#             # -------------------------------------------------------------
#             # COGS in company currency
#             # -------------------------------------------------------------

#             cogs_company = cogs_company_amounts.get(
#                 invoice_line.id,
#                 0.0,
#             )

#             # -------------------------------------------------------------
#             # Convert COGS from company currency to invoice currency.
#             # -------------------------------------------------------------

#             cogs_invoice_currency = company.currency_id._convert(
#                 cogs_company,
#                 invoice_currency,
#                 company,
#                 conversion_date,
#             )

#             # -------------------------------------------------------------
#             # Line revenue
#             #
#             # revenue_amount comes from account.move.line.price_subtotal
#             # so discounts are already included and taxes are excluded.
#             # -------------------------------------------------------------

#             revenue = record.revenue_amount or 0.0

#             # -------------------------------------------------------------
#             # Line margin
#             # -------------------------------------------------------------

#             line_margin = revenue - cogs_invoice_currency

#             if not invoice_currency.is_zero(revenue):
#                 line_margin_percentage = (
#                     line_margin / revenue
#                 ) * 100.0
#             else:
#                 line_margin_percentage = 0.0

#             # -------------------------------------------------------------
#             # Total invoice COGS
#             # -------------------------------------------------------------

#             total_cogs_company = invoice_total_cogs_company.get(
#                 invoice.id,
#                 0.0,
#             )

#             total_cogs_invoice_currency = company.currency_id._convert(
#                 total_cogs_company,
#                 invoice_currency,
#                 company,
#                 conversion_date,
#             )

#             # -------------------------------------------------------------
#             # Total invoice revenue
#             # -------------------------------------------------------------

#             total_revenue = sum(
#                 invoices.filtered(
#                     lambda inv: inv.id == invoice.id
#                 ).invoice_line_ids.filtered(
#                     lambda line:
#                     line.display_type == "product"
#                     and line.move_id.state == "posted"
#                     and line.move_id.move_type == "out_invoice"
#                 ).mapped("price_subtotal")
#             )

#             # -------------------------------------------------------------
#             # Total margin
#             # -------------------------------------------------------------

#             total_margin = (
#                 total_revenue
#                 - total_cogs_invoice_currency
#             )

#             if not invoice_currency.is_zero(total_revenue):
#                 total_margin_percentage = (
#                     total_margin / total_revenue
#                 ) * 100.0
#             else:
#                 total_margin_percentage = 0.0

#             # -------------------------------------------------------------
#             # Assign values
#             # -------------------------------------------------------------

#             record.cogs = cogs_invoice_currency
#             record.line_margin_amount = line_margin
#             record.line_margin_percentage = line_margin_percentage

#             record.total_cogs = total_cogs_invoice_currency
#             record.total_margin_amount = total_margin
#             record.total_margin_percentage = total_margin_percentage

#     # -------------------------------------------------------------------------
#     # SQL VIEW
#     # -------------------------------------------------------------------------

#     def init(self):

#         tools.drop_view_if_exists(
#             self.env.cr,
#             self._table,
#         )

#         self.env.cr.execute("""
#             CREATE VIEW invoice_margin_report AS (

#                 SELECT

#                     aml.id AS id,

#                     -- -----------------------------------------------------
#                     -- Invoice
#                     -- -----------------------------------------------------

#                     am.id AS invoice_id,

#                     am.name AS invoice_number,

#                     am.invoice_date AS invoice_date,

#                     am.partner_id AS customer_id,

#                     am.company_id AS company_id,

#                     am.currency_id AS currency_id,

#                     -- -----------------------------------------------------
#                     -- Product
#                     -- -----------------------------------------------------

#                     aml.product_id AS product_id,

#                     aml.quantity AS quantity,

#                     aml.price_unit AS selling_price,

#                     -- -----------------------------------------------------
#                     -- Revenue
#                     --
#                     -- price_subtotal:
#                     --     discount included
#                     --     tax excluded
#                     -- -----------------------------------------------------

#                     aml.price_subtotal AS revenue_amount,

#                     -- -----------------------------------------------------
#                     -- Invoice total revenue
#                     --
#                     -- Window function prevents duplication.
#                     -- -----------------------------------------------------

#                     SUM(aml.price_subtotal)
#                         OVER (
#                             PARTITION BY aml.move_id
#                         ) AS total_revenue,

#                     -- -----------------------------------------------------
#                     -- Sales Order
#                     --
#                     -- One invoice line can be linked to multiple SO lines.
#                     -- STRING_AGG prevents duplicate report rows.
#                     -- -----------------------------------------------------

#                     (
#                         SELECT STRING_AGG(
#                             DISTINCT so.name,
#                             ', '
#                             ORDER BY so.name
#                         )
#                         FROM sale_order_line sol
#                         JOIN sale_order so
#                             ON so.id = sol.order_id
#                         JOIN sale_order_line_invoice_rel rel
#                             ON rel.order_line_id = sol.id
#                         WHERE rel.invoice_line_id = aml.id
#                     ) AS sale_order_number

#                 FROM account_move_line aml

#                 JOIN account_move am
#                     ON am.id = aml.move_id

#                 WHERE

#                     am.move_type = 'out_invoice'

#                     AND am.state = 'posted'

#                     AND aml.display_type = 'product'

#                     AND aml.product_id IS NOT NULL

#             )
#         """)
