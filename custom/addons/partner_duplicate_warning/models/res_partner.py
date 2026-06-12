from odoo import models, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange('name')
    def _onchange_duplicate_name_warning(self):
        if not self.name:
            return

        duplicate = self.env['res.partner'].search([
            ('id', '!=', self.id),
            ('name', '=ilike', self.name.strip()),
        ], limit=1)

        if duplicate:
            return {
                'warning': {
                    'title': _('Duplicate Contact'),
                    'message': _(
                        "A contact with this name already exists.\n\n"
                        "Existing Contact: %s"
                    ) % duplicate.display_name,
                }
            }