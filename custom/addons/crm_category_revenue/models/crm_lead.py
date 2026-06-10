# Version 1
# from odoo import models, fields, api


# class CrmLead(models.Model):
#     _inherit = "crm.lead"

#     category_line_ids = fields.One2many(
#         "crm.lead.category.line",
#         "lead_id",
#         string="Category Lines"
#     )

#     total_category_amount = fields.Float(
#         string="Total Amount",
#         compute="_compute_total_amount",
#         store=True,
#     )

#     @api.depends("category_line_ids.amount")
#     def _compute_total_amount(self):
#         for lead in self:
#             total = sum(lead.category_line_ids.mapped("amount"))

#             lead.total_category_amount = total
#             lead.expected_revenue = total


# from odoo import models, fields, api


# class CrmLead(models.Model):
#     _inherit = "crm.lead"

#     category_line_ids = fields.One2many(
#         "crm.lead.category.line",
#         "lead_id",
#         string="Category Details"
#     )

#     total_category_amount = fields.Float(
#         string="Total Amount",
#         compute="_compute_total_amount",
#         store=True,
#     )

#     category_names = fields.Char(
#         string="Categories",
#         compute="_compute_category_names",
#         store=True,
#     )

#     @api.depends("category_line_ids.amount")
#     def _compute_total_amount(self):
#         for lead in self:
#             total = sum(lead.category_line_ids.mapped("amount"))
#             lead.total_category_amount = total

#             # Sync Expected Revenue
#             lead.expected_revenue = total

#     @api.depends("category_line_ids.category_id")
#     def _compute_category_names(self):
#         for lead in self:
#             lead.category_names = ", ".join(
#                 lead.category_line_ids.mapped("category_id.name")
#             )

# Version 2

# from odoo import models, fields, api


# class CrmLead(models.Model):
#     _inherit = "crm.lead"

#     category_line_ids = fields.One2many(
#         "crm.lead.category.line",
#         "lead_id",
#         string="Category Details"
#     )

#     total_category_amount = fields.Float(
#         string="Total Amount",
#         compute="_compute_total_amount",
#         store=True,
#     )

#     category_names = fields.Char(
#         string="Categories",
#         compute="_compute_category_names",
#         store=True,
#     )

#     @api.depends(
#         "category_line_ids.amount",
#         "category_line_ids.status"
#     )
#     def _compute_total_amount(self):
#         for lead in self:

#             total_amount = sum(
#                 lead.category_line_ids.mapped("amount")
#             )

#             win_amount = sum(
#                 lead.category_line_ids.filtered(
#                     lambda l: l.status == "win"
#                 ).mapped("amount")
#             )

#             lead.total_category_amount = total_amount

#             # Expected Revenue = only Win Amount
#             lead.expected_revenue = win_amount

#     @api.depends("category_line_ids.category_id")
#     def _compute_category_names(self):
#         for lead in self:
#             lead.category_names = ", ".join(
#                 lead.category_line_ids.mapped("category_id.name")
#             )

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = "crm.lead"

    category_line_ids = fields.One2many(
        "crm.lead.category.line",
        "lead_id",
        string="Category Details"
    )

    total_category_amount = fields.Float(
        string="Total Amount",
        compute="_compute_total_amount",
        store=True,
    )

    category_names = fields.Char(
        string="Categories",
        compute="_compute_category_names",
        store=True,
    )

    @api.depends(
        "category_line_ids.amount",
        "category_line_ids.status"
    )
    def _compute_total_amount(self):
        for lead in self:

            total_amount = sum(
                lead.category_line_ids.mapped("amount")
            )

            won_amount = sum(
                lead.category_line_ids.filtered(
                    lambda l: l.status == "won"
                ).mapped("amount")
            )

            lead.total_category_amount = total_amount

            # Expected Revenue = Won only
            lead.expected_revenue = won_amount

    @api.depends("category_line_ids.category_id")
    def _compute_category_names(self):
        for lead in self:
            lead.category_names = ", ".join(
                lead.category_line_ids.mapped("category_id.name")
            )
