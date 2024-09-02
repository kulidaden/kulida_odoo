from odoo import fields,models
from datetime import datetime, timedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description='This module created by Kulida Denys'

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
