# from odoo import models, fields, api


# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     quotation_number = fields.Char(
#         string="Quotation Number",
#         copy=False,
#         readonly=True,
#     )

#     so_number = fields.Char(
#         string="SO Number",
#         copy=False,
#         readonly=True,
#     )

#     display_number = fields.Char(
#         string="Display Number",
#         compute="_compute_display_number",
#         store=True,
#     )

#     @api.depends("quotation_number", "so_number", "state")
#     def _compute_display_number(self):
#         for rec in self:
#             if rec.state in ["sale", "done"]:
#                 rec.display_number = rec.so_number
#             else:
#                 rec.display_number = rec.quotation_number

#     @api.model_create_multi
#     def create(self, vals_list):

#         for vals in vals_list:

#             if vals.get("name", "New") == "New":

#                 next_seq = self.env["ir.sequence"].next_by_code(
#                     "sale.quotation.sequence"
#                 )

#                 vals["quotation_number"] = (
#                     f"QU/{self._get_financial_year()}/{next_seq[-3:]}"
#                 )

#                 vals["name"] = vals["quotation_number"]

#         return super().create(vals_list)

#     def action_confirm(self):

#         res = super().action_confirm()

#         for order in self:

#             if not order.so_number:

#                 next_seq = self.env["ir.sequence"].next_by_code(
#                     "sale.order.confirmed.sequence"
#                 )

#                 order.so_number = (
#                     f"SO/{order._get_financial_year()}/{next_seq[-3:]}"
#                 )

#                 # Main official number
#                 order.name = order.so_number

#                 # UPDATE DELIVERY SOURCE DOCUMENT
#                 for picking in order.picking_ids:
#                     picking.origin = order.so_number

#                 # UPDATE INVOICE SOURCE DOCUMENT
#                 for invoice in order.invoice_ids:
#                     invoice.invoice_origin = order.so_number

#         return res

#     def _get_financial_year(self):

#         today = fields.Date.today()

#         year = today.year

#         if today.month >= 4:
#             start = str(year)[-2:]
#             end = str(year + 1)[-2:]
#         else:
#             start = str(year - 1)[-2:]
#             end = str(year)[-2:]

#         return f"{start}-{end}"


# from odoo import models, fields, api


# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     quotation_number = fields.Char(
#         string="Quotation Number",
#         copy=False,
#         readonly=True,
#     )

#     so_number = fields.Char(
#         string="SO Number",
#         copy=False,
#         readonly=True,
#     )

#     display_number = fields.Char(
#         string="Display Number",
#         compute="_compute_display_number",
#         store=True,
#     )

#     @api.depends("quotation_number", "so_number", "state")
#     def _compute_display_number(self):
#         for rec in self:
#             if rec.state in ["sale", "done"]:
#                 rec.display_number = rec.so_number
#             else:
#                 rec.display_number = rec.quotation_number

#     @api.model_create_multi
#     def create(self, vals_list):

#         for vals in vals_list:

#             if vals.get("name", "New") == "New":

#                 fy = self._get_financial_year()

#                 next_number = self._get_next_quotation_sequence(fy)

#                 quotation_sequence = f"IP/QU/{fy}/{next_number}"

#                 vals["quotation_number"] = quotation_sequence
#                 vals["name"] = quotation_sequence

#         return super().create(vals_list)

#     def action_confirm(self):

#         res = super().action_confirm()

#         for order in self:

#             if not order.so_number:

#                 fy = order._get_financial_year()

#                 next_number = order._get_next_so_sequence(fy)

#                 so_sequence = f"IP/SO/{fy}/{next_number}"

#                 order.so_number = so_sequence

#                 # Main official number
#                 order.name = so_sequence

#                 # UPDATE DELIVERY SOURCE DOCUMENT
#                 for picking in order.picking_ids:
#                     picking.origin = so_sequence

#                 # UPDATE INVOICE SOURCE DOCUMENT
#                 for invoice in order.invoice_ids:
#                     invoice.invoice_origin = so_sequence

#         return res

#     def _get_financial_year(self):

#         today = fields.Date.today()

#         year = today.year

#         if today.month >= 4:
#             fy = str(year)[-2:]
#         else:
#             fy = str(year - 1)[-2:]

#         return fy

#     def _get_next_quotation_sequence(self, fy):

#         last_order = self.search([
#             ("quotation_number", "like", f"IP/QU/{fy}/")
#         ], order="id desc", limit=1)

#         if last_order and last_order.quotation_number:

#             last_number = int(
#                 last_order.quotation_number.split("/")[-1]
#             )

#             next_number = last_number + 1

#         else:
#             next_number = 1

#         return str(next_number).zfill(3)

#     def _get_next_so_sequence(self, fy):

#         last_order = self.search([
#             ("so_number", "like", f"IP/SO/{fy}/")
#         ], order="id desc", limit=1)

#         if last_order and last_order.so_number:

#             last_number = int(
#                 last_order.so_number.split("/")[-1]
#             )

#             next_number = last_number + 1

#         else:
#             next_number = 1

#         return str(next_number).zfill(3)

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    quotation_number = fields.Char(readonly=True, copy=False)
    so_number = fields.Char(readonly=True, copy=False)

    display_number = fields.Char(
        compute="_compute_display_number",
        store=True
    )

    @api.depends("state", "quotation_number", "so_number")
    def _compute_display_number(self):
        for rec in self:
            rec.display_number = rec.so_number if rec.state in ["sale", "done"] else rec.quotation_number

    # -------------------------
    # QUOTATION CREATE
    # -------------------------
    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("name", "New") == "New":

                seq = self.env["ir.sequence"].next_by_code("sale.quotation.sequence")

                vals["quotation_number"] = seq
                vals["name"] = seq   # important for stock/invoice linkage

        return super().create(vals_list)

    # -------------------------
    # CONFIRM SALE ORDER
    # -------------------------
    def action_confirm(self):

        res = super().action_confirm()

        for order in self:

            if not order.so_number:

                seq = self.env["ir.sequence"].next_by_code("sale.order.sequence")

                order.so_number = seq

                # IMPORTANT: make SO number official reference
                order.name = seq

                # Update delivery orders
                for picking in order.picking_ids:
                    picking.origin = seq

                # Update invoices
                for invoice in order.invoice_ids:
                    invoice.invoice_origin = seq

        return res
