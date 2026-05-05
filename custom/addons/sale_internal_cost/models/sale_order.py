from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight = fields.Monetary(string="Freight")
    duty = fields.Monetary(string="Duty")
    misc = fields.Monetary(string="Miscellaneous")

    @api.onchange('freight', 'duty', 'misc')
    def _onchange_update_charge_line(self):
        """Automatically manages the internal charge line."""
        for order in self:
            total_charge = (order.freight or 0.0) + (order.duty or 0.0) + (order.misc or 0.0)
            
            # Find existing charge line using the boolean flag
            charge_line = order.order_line.filtered(lambda l: l.x_is_charge_line)
            
            if total_charge > 0:
                if charge_line:
                    # Update price if line exists
                    charge_line[0].price_unit = total_charge
                else:
                    # Create new line if it doesn't exist
                    new_line_vals = {
                        'name': 'Internal Charges (Freight, Duty, Misc)',
                        'product_uom_qty': 1.0,
                        'price_unit': total_charge,
                        'tax_ids': [(6, 0, [])],  # No taxes applied
                        'x_is_charge_line': True,
                    }
                    order.order_line = [(0, 0, new_line_vals)]
            else:
                # If charges become 0, remove the line
                if charge_line:
                    order.order_line -= charge_line

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_is_charge_line = fields.Boolean(string="Is Charge Line", default=False)
