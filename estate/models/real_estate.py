from odoo import models, fields, api, _, exceptions


def get_availability_date(model):
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    current_date = datetime.today()
    three_months_ago = current_date - relativedelta(months=3)

    return three_months_ago


class RealEstate(models.Model):
    _name = "real.estate"
    _description = "Real Estate"
    _order = "id desc"

    offer_ids = fields.One2many("real.estate.property.offer", "property_id")
    property_type_id = fields.Many2one("real.estate.type")
    property_tags_ids = fields.Many2many("real.estate.property.tag")
    title = fields.Char(string="Title", default="Unknown", required=True)
    last_seen = fields.Datetime(string="Last Seen", copy=False, default=fields.Datetime.now)
    description = fields.Text(string="Description")
    postalcode = fields.Char(string="Postal Code")
    date_availability = fields.Date(string="Date Available", copy=False, default=get_availability_date)
    expected_price = fields.Float(string="Expected Pricee")
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=3)
    living_area = fields.Integer(string="Living Area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden", default=True)
    garden_area = fields.Integer(string="Garden Area")
    garden_orientation = fields.Selection([
        ('N', 'North'),
        ('S', 'South'),
        ('E', 'East'),
        ('W', 'West'),
    ], string="Garden Orientation")
    available = fields.Boolean(string="Available", default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ("sold", "Sold"),
        ("canceled", "Canceled")
        ], string="State", default='new', copy=False, readonly=True)

    partner_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, default=lambda self: self.env.user)
    total_area = fields.Integer(string="Total Area", compute="_compute_total_area")
    best_price = fields.Integer(string="Best Price", compute="_compute_best_price", store=True)

    _sql_constraints = [
        ('check_expected_price', 'CHECK(real_estate.expected_price >= 0)',
         'The expected price must be strictly positive'),
        ('check_selling_price', 'CHECK(real_estate.selling_price >= 0)',
         'The selling price must be strictly positive'),
        ('check_living_area', 'CHECK(real_estate.living_area >= 0)',
         'The living area must be strictly positive'),


    ]

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('expected_price', 'offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max([record.expected_price, *[offer.price for offer in record.offer_ids]])


    def property_sold(self):
        """
        Sets the state of the property to 'sold' if it is currently 'new' or 'offer_accepted'.
        If the property is already 'canceled', returns a warning message.

        :return: If the property is 'canceled', returns a warning message. Otherwise, returns None.
        :rtype: dict or None
        """
        if self.state == "new" or self.state == "offer_accepted":
            self.state = 'sold'
            self.available = False
        elif self.state == "canceled":
            return models.ValidationError('You cannot sell a canceled property')
        else:
            return False

    def property_canceled(self):
        """
        Sets the state of the property to 'canceled' if it is currently 'new'.
        If the property is already 'sold', returns a warning message.

        :return: If the property is 'sold', returns a warning message. Otherwise, returns None.
        :rtype: dict or None
        """
        if self.state == "new":
            self.state = 'canceled'
            self.available = False
        elif self.state == "sold":
            return models.ValidationError('You cannot cancel a property that has been sold')

    def unlink(self):
        # Delete associated offers before deleting the property
        for property_record in self:
            property_record.offer_ids.unlink()
        return super(RealEstate, self).unlink()