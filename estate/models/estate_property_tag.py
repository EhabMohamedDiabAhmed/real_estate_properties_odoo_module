from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "real.estate.property.tag"
    _description = "this is property tag"
    _order = "name desc"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")
