from odoo import fields,models
from datetime import datetime, timedelta


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'

    price = fields.Float(string='Price', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], string='Status', default='accepted')
    property_id = fields.Many2one('estate.property', string='Property', required=True)


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"

    name = fields.Char(string="Name", required=True)


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    name = fields.Char(string="Name", required=True)


class EstateProperty(models.Model):
    _name = "estate.property"
    _description='Property'

    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)
    name = fields.Char(string="Estate", required=True, default='Unknown')
    date_availability = fields.Date(string="Availability Date",
                                    default=lambda self: datetime.today() + timedelta(days=90),copy=False)
    postcode = fields.Char(string="Postcode")
    expected_price = fields.Float(string="Expected Price", required=True)
    garage = fields.Boolean(string="Garage")
    selling_price = fields.Float(string="Selling Price",readonly=True)
    garden = fields.Boolean(string="Garden")
    bedrooms = fields.Integer(string="Bedrooms")
    active=fields.Boolean(string='Active',default=True)
    living_area = fields.Integer(string="Living Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ('north', "North"),
            ('south', "South"),
            ('east', "East"),
            ('west', "West")
        ],
    )
    facades = fields.Integer(string="Facades")
    state=fields.Selection(string='State',required=True,copy=False,default="new",
                           selection=[
                               ('new',"New"),
                               ('offer received',"Offer Received"),
                               ('offer accepted',"Offer Accepted"),
                               ('sold',"Sold"),
                               ('canceled',"Canceled")
                           ]
    )
    garden_area = fields.Integer(string="Garden Area (sqm)")
    description = fields.Text(string="Description")
    property_type_id = fields.Many2one('estate.property.type', string="Property Type")
    buyer_id = fields.Many2one('res.partner', string="Buyer")
    seller_id = fields.Many2one('res.partner', string="Salesman", index=True, tracking=True, default=lambda self: self.env.user.partner_id.id)
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')












