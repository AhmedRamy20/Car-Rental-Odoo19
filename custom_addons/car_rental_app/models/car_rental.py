from odoo import fields, models
from odoo.exceptions import UserError


class CarRental(models.Model):
    _name = "car.rental.car"
    _description = "Car rental"
    
    
    
    
    name = fields.Char(string="Car Name",required=True)
    car_model = fields.Char(string="Car Model",required=True)
    car_brand = fields.Char(string="Car Brand",required=True)
    license_plate = fields.Char(string="License Plate", required=True)
    
    manufacturing_year = fields.Integer(string="Manufacturing Year",help="Manufacturing year of the car")

    car_state = fields.Selection([
        ("available","Available"),
        ("rented","Rented"),
        ("damaged","Damaged"),
    ],string="Status", default='available', required=True)
    
   
    reservation_ids = fields.One2many("car.rental.reservation","car_id")
    
    is_manager = fields.Boolean(compute="_compute_is_a_manager")
    
    # here we want to know if the currnet user is a manager of not so that we can make the reserve car button invisible from the manager cause we did make in security that manager inherits the user group also
    def _compute_is_a_manager(self):
        manager = self.env.user.has_group("car_rental_app.car_rental_manager_group")
        for rec in self:
            rec.is_manager = manager
    
    def action_reserve(self):
        for rec in self:
            if rec.car_state != "available":
                raise UserError("This car is not available for reservation.")
            # create a reservation
            self.env["car.rental.reservation"].create({
                "car_id": rec.id
            })
            # change the car state to rented
            # rec.car_state = "rented"
            # bit we want to sort of bybass the write permission for the users (cause i did make users permissions so they can not write or do anything other tan read)
            rec.sudo().write({
                "car_state": "rented",
            })