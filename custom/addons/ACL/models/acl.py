from odoo import models, fields

class ACL(models.Model):
    _name = "acl"
    _description = "ACL Management"

    name = fields.Char()