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
    
    
    
    
    def action_reserve(self):
        for rec in self:
            if rec.car_state != "available":
                raise UserError("This car is not available for reservation.")
            # create a reservation
            self.env["car.rental.reservation"].create({
                "car_id": rec.id
            })
            # change the car state to rented
            rec.car_state = "rented"