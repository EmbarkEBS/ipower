# from odoo import models, fields, api


# class AccountMove(models.Model):
#     _inherit = "account.move"

#     company_bank_id = fields.Many2one(
#         "res.partner.bank",
#         string="Company Bank Account",
#         copy=False,
#     )

#     bank_display_details = fields.Html(
#         string="Bank Details",
#         compute="_compute_bank_display_details",
#     )

#     @api.onchange("company_id")
#     def _onchange_company_id_bank(self):
#         return {
#             "domain": {
#                 "company_bank_id": [
#                     ("partner_id", "=", self.company_id.partner_id.id)
#                 ]
#             }
#         }

#     @api.depends("company_bank_id")
#     def _compute_bank_display_details(self):
#         for move in self:
#             bank = move.company_bank_id

#             if not bank:
#                 move.bank_display_details = False
#                 continue

#             move.bank_display_details = """
#                 <b>Bank Name:</b> %s<br/>
#                 <b>Account Number:</b> %s<br/>
#                 <b>IBAN Number:</b> %s<br/>
#                 <b>Account Holder:</b> %s
#             """ % (
#                 bank.bank_id.name or "",
#                 bank.acc_number or "",
#                 bank.iban or "",
#                 bank.partner_id.name or "",
#             )

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    available_company_bank_ids = fields.Many2many(
        "res.partner.bank",
        compute="_compute_available_company_bank_ids",
    )

    company_bank_id = fields.Many2one(
        "res.partner.bank",
        string="Company Bank Account",
        domain="[('id', 'in', available_company_bank_ids)]",
        copy=False,
    )

    bank_display_details = fields.Html(
        string="Bank Details",
        compute="_compute_bank_display_details",
    )

    @api.depends("company_id")
    def _compute_available_company_bank_ids(self):
        for rec in self:
            rec.available_company_bank_ids = self.env["res.partner.bank"].search([
                ("partner_id", "=", rec.company_id.partner_id.id)
            ])

    @api.depends("company_bank_id")
    def _compute_bank_display_details(self):
        for rec in self:
            bank = rec.company_bank_id

            if not bank:
                rec.bank_display_details = False
                continue

            rec.bank_display_details = """
                <b>Bank Name:</b> %s<br/>
                <b>Account Number:</b> %s<br/>
                <b>IBAN Number:</b> %s<br/>
                <b>Account Holder:</b> %s
            """ % (
                bank.bank_id.name or "",
                bank.acc_number or "",
                bank.iban or "",
                bank.partner_id.name or "",
            )
