from odoo import models, fields


class RealEstateType(models.Model):
    _name = "real.estate.type"
    _description = "this is the type of the real estate"
    _order = "name desc"

    # name = fields.Char(string="property type", required=True)
    name = fields.Char(string="Property Type", required=True)
    properties_ids = fields.One2many("real.estate", "property_type_id")
    sequence = fields.Integer("Sequence", default=10, help="Used to order properties by type in task views")
    offer_count = fields.Integer(compute="_compute_offer_count")

    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = self.env["real.estate.property.offer"].search_count(
                [("property_id", "in", rec.properties_ids.ids)]
            )

    def action_view_offers(self):

        return {
            "name": "Offers",
            "type": "ir.actions.act_window",
            "res_model": "real.estate.property.offer",
            "view_mode": "tree",
            "domain": [("property_id", "in", self.properties_ids.ids)],
        }

    _sql_constraints = [
        ('check_name', 'UNIQUE(name)', 'The name must be unique'),
    ]
