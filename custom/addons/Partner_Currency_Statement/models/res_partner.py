from odoo import models

class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_print_currency_statement(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Currency Statement",
            "res_model": "partner.currency.statement.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": self.id,
            },
        }