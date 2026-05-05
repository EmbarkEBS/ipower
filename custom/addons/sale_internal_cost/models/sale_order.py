from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight = fields.Monetary(string="Freight")
    duty = fields.Monetary(string="Duty")
    misc = fields.Monetary(string="Miscellaneous")

    @api.onchange('freight', 'duty', 'misc')
    def _onchange_update_charge_line(self):
        """Adds, updates, or REMOVES the internal charge line."""
        for order in self:
            total_charge = (order.freight or 0.0) + (order.duty or 0.0) + (order.misc or 0.0)
            
            # Find the special charge line using the boolean flag
            charge_line = order.order_line.filtered(lambda l: l.x_is_charge_line)
            
            if total_charge > 0:
                if charge_line:
                    # Update price on the existing line
                    charge_line[0].price_unit = total_charge
                else:
                    # Create the new line
                    new_line_vals = {
                        'name': 'Internal Charges (Freight, Duty, Misc)',
                        'product_uom_qty': 1.0,
                        'price_unit': total_charge,
                        'tax_ids': [(6, 0, [])], # No taxes
                        'x_is_charge_line': True,
                    }
                    # Command (0, 0, vals) adds the line
                    order.order_line = [(0, 0, new_line_vals)]
            else:
                # IF CHARGE IS 0: Remove the line from the UI
                if charge_line:
                    # We use command (2, ID, 0) to delete the line from the view
                    # We loop in case there are multiple by mistake
                    commands = []
                    for line in charge_line:
                        # If the line exists in DB, use ID. If it's new (Virtual), use _origin
                        line_id = line.id.origin if hasattr(line.id, 'origin') else line.id
                        commands.append((2, line_id, 0))
                    order.order_line = commands

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_is_charge_line = fields.Boolean(string="Is Charge Line", default=False)
