from odoo import fields, models,api
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
    @api.depends_context("uid")
    def _compute_is_a_manager(self):
        manager = self.env.user.has_group("car_rental_app.car_rental_manager_group")
        for rec in self:
            rec.is_manager = manager
    
    # method for reserving car
    def action_reserve(self):
        for rec in self:
            if rec.car_state != "available":
                raise UserError("This car is not available for reservation.")
            # we dud this also so the user will not have any chance to change it via any other interface
            if not rec.env.user.has_group("car_rental_app.car_rental_user_group"):
                raise UserError("Only Users can Reserve and Rent Cars.")
            
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



    # method for making a car as damage
    def action_damage(self):
        for rec in self:
            # this incase we did not make the button invisible BUT we will :)
            if rec.car_state == "damaged":
                raise UserError("You can't mark an Already damaged car as damaged")
            
            if rec.car_state == "rented":
                raise UserError("You can't mark a rented car as damaged")
            # users can't mark cars as damaged via any other interface so we make sure here  by checking if this user or manager
            if not rec.env.user.has_group("car_rental_app.car_rental_manager_group"):
                raise UserError("Only Mangagers Can Mark This Car as Damaged.")
            
            # mark car as damaged
            rec.car_state = "damaged"
            
    
     # method for making a car as available
    def action_restore_available(self):
        for rec in self:

            # users also can not restore a damaged car to be avail
            # users can not restore car to available via any interface only manager can do that
            if not rec.env.user.has_group("car_rental_app.car_rental_manager_group"):
                    raise UserError("Only Mangagers Can Mark This Car as Available.")
            
            if rec.car_state != "damaged":
                raise UserError("Only damaged cars can be restored.")
            
            rec.car_state = "available"
    
    
    # this action to view the list of reservation for this specific car 
    def action_view_reservations(self):
        self.ensure_one()
        if not self.env.user.has_group("car_rental_app.car_rental_manager_group"):
            raise UserError("Only managers can view car reservation history.")
        return {
            "type": "ir.actions.act_window",
            "name": "Reservations",
            "res_model": "car.rental.reservation",
            "view_mode": "list,form",
            "domain": [("car_id", "=", self.id)],
            "context": {"default_car_id": self.id},
        }

    count = fields.Integer(compute="_compute_reservation_count")
    
    @api.depends("reservation_ids")
    def _compute_reservation_count(self):
        for rec in self:
            rec.count = len(rec.reservation_ids)