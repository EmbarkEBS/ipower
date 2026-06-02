from odoo import models
import logging

_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def action_check_low_stock_alerts(self):

        _logger.info("🔥 LOW STOCK ALERT STARTED")

        activity_type = self.env.ref('mail.mail_activity_data_warning')
        group = self.env.ref('stock.group_stock_manager')

        users = group.users if hasattr(group, 'users') and group.users else self.env.user

        orderpoints = self.search([])

        _logger.info(f"Orderpoints found: {len(orderpoints)}")

        for rule in orderpoints:
            product = rule.product_id

            if not product:
                continue

            # SAFE STOCK CHECK
            quant = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id', 'child_of', rule.location_id.id),
            ])

            qty_available = sum(quant.mapped('quantity'))

            _logger.info(f"{product.display_name} qty = {qty_available}")

            if qty_available >= rule.product_min_qty:
                continue

            # Create alert for each inventory admin
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': self.env['ir.model']._get('product.product').id,
                    'res_id': product.id,
                    'activity_type_id': activity_type.id,
                    'summary': 'Low Stock Alert',
                    'note': f"""
⚠ Low Stock Alert

Product: {product.display_name}
Available Qty: {qty_available}
Minimum Qty: {rule.product_min_qty}
Warehouse: {rule.warehouse_id.name}
                    """,
                    'user_id': user.id,
                })

        _logger.info("🔥 LOW STOCK ALERT COMPLETED")
        return True
