# Version 1 
# from odoo import models, fields


# class CrmLeadCategoryLine(models.Model):
#     _name = "crm.lead.category.line"
#     _description = "CRM Lead Category Line"

#     lead_id = fields.Many2one(
#         "crm.lead",
#         required=True,
#         ondelete="cascade"
#     )

#     category_id = fields.Many2one(
#         "product.category",
#         string="Product Category",
#         required=True
#     )

#     status = fields.Selection(
#         [
#             ("win", "Win"),
#             ("progress", "In Progress"),
#             ("lost", "Lost"),
#         ],
#         required=True,
#         default="progress"
#     )

#     amount = fields.Float(
#         string="Amount",
#         required=True
#     )

#     _sql_constraints = [
#         (
#             "unique_category_per_lead",
#             "unique(lead_id, category_id)",
#             "Category already exists in this lead."
#         )
#     ]

# from odoo import models, fields


# class CrmLeadCategoryLine(models.Model):
#     _name = "crm.lead.category.line"
#     _description = "CRM Lead Category Line"

#     lead_id = fields.Many2one(
#         "crm.lead",
#         string="Lead",
#         required=True,
#         ondelete="cascade"
#     )

#     category_id = fields.Many2one(
#         "product.category",
#         string="Product Category",
#         required=True
#     )

#     status = fields.Selection(
#         [
#             ("win", "Win"),
#             ("progress", "In Progress"),
#             ("lost", "Lost"),
#         ],
#         string="Status",
#         required=True,
#         default="progress"
#     )

#     amount = fields.Float(
#         string="Amount",
#         required=True
#     )

#     lead_total_amount = fields.Float(
#     related="lead_id.total_category_amount",
#     string="Lead Total Amount",
#     store=True,
#     )

#     _sql_constraints = [
#         (
#             "unique_category_per_lead",
#             "unique(lead_id, category_id)",
#             "Category already exists in this lead."
#         )
#     ]

# Version 2

# from odoo import models, fields


# class CrmLeadCategoryLine(models.Model):
#     _name = "crm.lead.category.line"
#     _description = "CRM Lead Category Line"

#     lead_id = fields.Many2one(
#         "crm.lead",
#         required=True,
#         ondelete="cascade"
#     )

#     customer_id = fields.Many2one(
#         "res.partner",
#         related="lead_id.partner_id",
#         string="Customer",
#         store=True,
#     )

#     category_id = fields.Many2one(
#         "product.category",
#         string="Product Category",
#         required=True
#     )

#     status = fields.Selection(
#         [
#             ("win", "Win"),
#             ("progress", "In Progress"),
#             ("lost", "Lost"),
#         ],
#         required=True,
#         default="progress"
#     )

#     amount = fields.Float(
#         string="Amount",
#         required=True
#     )

#     _sql_constraints = [
#         (
#             "unique_category_per_lead",
#             "unique(lead_id, category_id)",
#             "Category already exists in this lead."
#         )
#     ]

from odoo import models, fields


class CrmLeadCategoryLine(models.Model):
    _name = "crm.lead.category.line"
    _description = "CRM Lead Category Line"

    lead_id = fields.Many2one(
        "crm.lead",
        required=True,
        ondelete="cascade"
    )

    customer_id = fields.Many2one(
        "res.partner",
        related="lead_id.partner_id",
        string="Customer",
        store=True,
    )

    category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        required=True
    )

    vendor_ids = fields.Many2one(
        "res.partner",
        "crm_category_vendor_rel",
        "line_id",
        "partner_id",
        string="Vendors",
        domain="[('supplier_rank', '>', 0)]"
    )

    status = fields.Selection(
        [
            ("active", "Active"),
            ("won", "Won"),
            ("lost", "Lost"),
        ],
        string="Status",
        required=True,
        default="active"
    )

    amount = fields.Float(
        string="Amount",
        required=True
    )

    _sql_constraints = [
        (
            "unique_category_per_lead",
            "unique(lead_id, category_id)",
            "Category already exists in this lead."
        )
    ]
