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

#             won_amount = sum(
#                 lead.category_line_ids.filtered(
#                     lambda l: l.status == "won"
#                 ).mapped("amount")
#             )

#             lead.total_category_amount = total_amount

#             # Expected Revenue = Won only
#             lead.expected_revenue = won_amount

#     @api.depends("category_line_ids.category_id")
#     def _compute_category_names(self):
#         for lead in self:
#             lead.category_names = ", ".join(
#                 lead.category_line_ids.mapped("category_id.name")
#             )

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    category_line_ids = fields.One2many(
        "crm.lead.category.line",
        "lead_id",
        string="Category Details"
    )

    total_category_amount = fields.Float(
        string="Won Amount Total",
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
            won_total = sum(
                lead.category_line_ids.filtered(
                    lambda l: l.status == "won"
                ).mapped("amount")
            )

            lead.total_category_amount = won_total

            # Expected Revenue = Won Amount Only
            lead.expected_revenue = won_total

    @api.depends("category_line_ids.category_id")
    def _compute_category_names(self):
        for lead in self:
            lead.category_names = ", ".join(
                lead.category_line_ids.mapped("category_id.name")
            )

    def _check_category_status_before_close(self):
        """
        Prevent opportunity from being moved to a Won/Closed stage
        when at least one category is still Active.
        """
        for lead in self:
            active_lines = lead.category_line_ids.filtered(
                lambda l: l.status == "active"
            )

            if active_lines:
                raise ValidationError(
                    _(
                        "Project cannot be closed.\n\n"
                        "All product categories must first be updated to Won or Lost."
                    )
                )

    def write(self, vals):
        if vals.get("stage_id"):
            stage = self.env["crm.stage"].browse(vals["stage_id"])

            # Custom Closed stage has Is Won checked
            if stage.exists() and stage.is_won:
                self._check_category_status_before_close()

        return super().write(vals)

    def action_set_won(self):
        self._check_category_status_before_close()
        return super().action_set_won()

    def action_set_won_rainbowman(self):
        self._check_category_status_before_close()
        return super().action_set_won_rainbowman()
