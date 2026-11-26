
from odoo import fields, models
from odoo.exceptions import UserError


class CarAssignRentalWizard(models.TransientModel):
    _name = "car.rental.wizard"
    _description = "Reserve Car for Customer Wizard"

    car_id = fields.Many2one(
        "car.rental.car",
        string="Car",
        required=True,
        readonly=True,
    )

    user_id = fields.Many2one(
        "res.users",
        string="Customer",
        required=True,
    )

    def action_confirm_reservation(self):
        self.ensure_one()
        
        if not self.env.user.has_group("car_rental_app.car_rental_manager_group"):
            raise UserError("Only managers can reserve cars for customers.")

        # see if can is avail
        if self.car_id.car_state != "available":
            raise UserError("This car is not available for reservation.")

        # Create reservation using the selected customer
        self.env["car.rental.reservation"].create({
            "car_id": self.car_id.id,
            "user_id": self.user_id.id,
        })

        # Update car state
        self.car_id.sudo().write({
            "car_state": "rented",
        })

        return {"type": "ir.actions.act_window_close"}
