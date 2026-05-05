from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight = fields.Monetary(string="Freight")
    duty = fields.Monetary(string="Duty")
    misc = fields.Monetary(string="Miscellaneous")

    @api.onchange('freight', 'duty', 'misc')
    def _onchange_update_charge_line(self):
        """Adds or updates a separate line for all internal charges."""
        for order in self:
            total_charge = (order.freight or 0.0) + (order.duty or 0.0) + (order.misc or 0.0)
            
            # Find our custom 'Internal Charge' line
            charge_line = order.order_line.filtered(lambda l: l.x_is_charge_line)
            
            if total_charge > 0:
                if charge_line:
                    # Update price on existing line
                    charge_line.price_unit = total_charge
                else:
                    # Create new line at the bottom. 
                    # FIX: Use 'tax_id' as correctly identified.
                    new_line_vals = {
                        'name': 'Internal Charges (Freight, Duty, Misc)',
                        'product_uom_qty': 1.0,
                        'price_unit': total_charge,
                        'tax_id': [(6, 0, [])], # No taxes applied
                        'x_is_charge_line': True,
                    }
                    order.order_line = [(0, 0, new_line_vals)]
            elif charge_line:
                # Remove the line if all charges are set to zero
                order.order_line = [(2, charge_line.id, 0)]

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Hidden field to identify our custom charge line
    x_is_charge_line = fields.Boolean(string="Is Charge Line", default=False)
