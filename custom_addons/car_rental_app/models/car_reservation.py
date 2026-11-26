from odoo import fields, models,api
from odoo.exceptions import UserError

class CarRentalReservation(models.Model):
    _name = "car.rental.reservation"
    _description = "Car Rental Reservation"
    _order = "reservation_date desc"

    ref = fields.Char(
        string="Reservation Reference",
        required=True,
        default="New",
        readonly=True,
        copy=False
    )

    car_id = fields.Many2one(
        "car.rental.car",
        string="Car",
        required=True,
        ondelete="restrict",
    )

    user_id = fields.Many2one(
        "res.users",
        string="Reserved By",
        required=True,
        readonly=True,
        default=lambda self: self.env.user,
    )

    reservation_date = fields.Datetime(
        string="Reservation Date",
        default=fields.Datetime.now,
        required=True,
    )

    return_request_date = fields.Datetime(
        string="Return Request Date",
        help="When the customer requested to return the car",
    )

    return_approve_date = fields.Datetime(
        string="Return Approval Date",
        help="When the manager approved the return",
    )

    reservation_state = fields.Selection([
        ("active", "Active"),
        ("return_requested", "Return Requested"),
        ("returned", "Returned"),
        ("cancelled", "Cancelled"),
    ], string="Reservation Status", default="active", required=True)

    
    
    is_manager = fields.Boolean(compute="_compute_is_a_manager")
    
    @api.depends_context("uid")
    def _compute_is_a_manager(self):
        manager = self.env.user.has_group("car_rental_app.car_rental_manager_group")
        for rec in self:
            rec.is_manager = manager




    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("ref", "New") == "New":
                vals["ref"] = self.env["ir.sequence"].next_by_code(
                    "car.rental.reservation"
                ) or "New"

        return super().create(vals_list)
    
    
    
    def car_request_return(self):
        for reserv in self: 
            
            #?? notice that the manager can see all the users can cause we did say in the security file that managers implies what is in user group but we did manage this using computed field in xml
            if reserv.env.user.has_group("car_rental_app.car_rental_manager_group"):
                raise UserError("Managers cannot request a return. Only users can.")
            # prevent cst to ask request return twice
            if reserv.reservation_state != "active":
                raise UserError("Only active reservations can request a return.")
            
            reserv.return_request_date = fields.Datetime.now()
            reserv.reservation_state = "return_requested"
            
            
            
    def car_approve_return(self):
        for reserv in self:
            if reserv.reservation_state != "return_requested":
                raise UserError("You must make a return request first.... ")
            
            # we did hide this button (approve requeset button) by specifying the group (manager group only) BUT we did this check also cause their is a possibility of calling this method from any other interface
            if not self.env.user.has_group("car_rental_app.car_rental_manager_group"):
                raise UserError("Only managers can approve returns.")
            
            reserv.return_approve_date = fields.Datetime.now()
            reserv.reservation_state = "returned"
            reserv.car_id.car_state = "available"