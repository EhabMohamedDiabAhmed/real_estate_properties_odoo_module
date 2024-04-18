from odoo import fields, models, api
from datetime import timedelta


class EstatePropertyOffer(models.Model):
    _name = "real.estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    # Price of the property
    price = fields.Float(string="Price", required=True)

    # Property being offered
    property_id = fields.Many2one("real.estate", string="Property", required=True)
    property_name = fields.Char(related="property_id.title")

    # Partner making the offer
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)

    # Status of the offer (accepted or refused)
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], string="Status")

    # Validity of the offer in days
    validity = fields.Integer(string="Validity (in days)")

    # Computed field for the deadline date of the offer
    date_deadline = fields.Date(string="Date Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    # Constraint to ensure that the price is strictly positive
    @api.constrains('price')
    def _check_price(self):
        if self.price <= .7*self.property_id.expected_price:
            raise models.ValidationError('The price must be at least 70% of the expected price')
        self.property_id.state = "offer_received"


    # Computed field to compute the deadline date based on the validity
    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.validity:
                record.date_deadline = fields.Date.today() + timedelta(days=record.validity)

    # Inverse method to update the validity based on the deadline date
    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - fields.Date.today()).days

    # Method to set the status of the offer as accepted
    def set_status_accepted(self):
        if self.price <= .9*self.property_id.expected_price:
            raise models.ValidationError('The price must be at least 90% of the expected price')
        else:
            if self.property_id.state not in ['sold', 'canceled']:
                self.property_id.state = "offer_accepted"
                self.status = 'accepted'
                self.property_id.selling_price = self.price
                self.property_id.partner_id = self.partner_id

    # Method to set the status of the offer as refused
    def set_status_refused(self):
        self.status = 'refused'

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The price must be strictly positive'),
    ]