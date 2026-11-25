from odoo import fields, models


class ExpenseVehicle(models.Model):
    _name = "expense.vehicle"
    _description = "Expense Vehicle"
    _rec_name = "vehicle_number"
    _order = "vehicle_number"

    vehicle_number = fields.Char(
        string="Vehicle Number",
        required=True,
        copy=False,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _vehicle_number_unique = models.Constraint(
        "UNIQUE(vehicle_number)",
        "This vehicle number already exists.",
    )
