# from odoo import api, fields, models


# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'

#     is_rfq = fields.Boolean(default=True)

#     @api.model_create_multi
#     def create(self, vals_list):

#         for vals in vals_list:
#             if vals.get('name', 'New') == 'New':
#                 vals['name'] = self.env['ir.sequence'].next_by_code(
#                     'purchase.rfq'
#                 ) or 'New'

#         return super().create(vals_list)

#     def button_confirm(self):

#         for order in self:
#             if order.is_rfq:
#                 order.name = self.env['ir.sequence'].next_by_code(
#                     'purchase.order.custom'
#                 )
#                 order.is_rfq = False

#         return super().button_confirm()
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_rfq = fields.Boolean(
        string="Is RFQ",
        default=True,
        copy=True
    )

    # =========================================================
    # CREATE RFQ
    # =========================================================
    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            # Get the company of the PO/RFQ being created
            company = self.env["res.company"].browse(
                vals.get(
                    "company_id",
                    self.env.company.id
                )
            )

            # -------------------------------------------------
            # Generate RFQ number for every NEW RFQ
            #
            # This covers:
            # 1. Manual RFQ
            # 2. RFQ created from Sales Order
            # 3. RFQ created by custom Create PO button
            # -------------------------------------------------
            if vals.get("name", "New") == "New":

                rfq_number = (
                    self.env["ir.sequence"]
                    .with_company(company)
                    .next_by_code("purchase.rfq")
                ) or "New"

                vals["name"] = rfq_number
                vals["is_rfq"] = True

        return super().create(vals_list)

    # =========================================================
    # DUPLICATE RFQ / PURCHASE ORDER
    # =========================================================
    def copy(self, default=None):

        self.ensure_one()

        default = dict(default or {})

        company = self.company_id

        # -------------------------------------------------
        # When duplicating an RFQ:
        # Generate a NEW RFQ number
        # -------------------------------------------------
        rfq_number = (
            self.env["ir.sequence"]
            .with_company(company)
            .next_by_code("purchase.rfq")
        ) or "New"

        default["name"] = rfq_number
        default["is_rfq"] = True

        return super().copy(default)

    # =========================================================
    # CONFIRM RFQ → PURCHASE ORDER
    # =========================================================
    def button_confirm(self):

        for order in self:

            if order.is_rfq:

                # ---------------------------------------------
                # Generate PO number using company's PO sequence
                # ---------------------------------------------
                po_number = (
                    self.env["ir.sequence"]
                    .with_company(order.company_id)
                    .next_by_code("purchase.order.custom")
                ) or "New"

                order.write({
                    "name": po_number,
                    "is_rfq": False,
                })

        return super().button_confirm()