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
            
            # Find the custom charge line using the boolean flag
            charge_line = order.order_line.filtered(lambda l: l.x_is_charge_line)
            
            if total_charge > 0:
                if charge_line:
                    # Update price on the existing charge line
                    charge_line.price_unit = total_charge
                else:
                    # Create a new line. NOTE: Using 'tax_id' (plural)
                    new_line_vals = {
                        'display_type': False,
                        'name': 'Internal Charges (Freight, Duty, Misc)',
                        'product_uom_qty': 1.0,
                        'price_unit': total_charge,
                        'tax_ids': [(6, 0, [])],  # This ensures the charge is NOT taxed
                        'x_is_charge_line': True,
                    }
                    # Command (0, 0, vals) adds the line to the quotation
                    order.order_line = [(0, 0, new_line_vals)]
            elif charge_line:
                # If all charges are removed, delete the line (Command 2)
                order.order_line = [(2, charge_line.id, 0)]

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Hidden field to identify the special charge line
    x_is_charge_line = fields.Boolean(string="Is Charge Line", default=False)
