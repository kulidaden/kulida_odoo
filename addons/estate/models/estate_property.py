from odoo import fields,models,api
from datetime import datetime, timedelta
from odoo.exceptions import *


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'

    price = fields.Float(string='Price', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    status = fields.Selection([
        (" "," "),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], string='Status', default=' ')
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    validity=fields.Integer(string='Validity',default=7)
    date_deadline=fields.Date(string="Deadline",compute='_compute_deadline',store=True,readonly=False)

    @api.depends('validity')
    def _compute_deadline(self):
        for deadline in self:
            deadline.date_deadline=datetime.today() + timedelta(days=deadline.validity)

    def action_accept(self):
        self.ensure_one()
        if self.price < 0:
            raise UserError('The expected price must be strictly positive!')
        if self.status == 'accepted':
            return
        if self.price<(self.property_id.expected_price*0.90):
            raise ValidationError("Selling price cannot be lower than 90% of the expected price.")
        self.write({'status': 'accepted'})
        other_offers = self.search([
            ('property_id', '=', self.property_id.id),
            ('id', '!=', self.id)
        ])
        other_offers.write({'status': 'refused'})
        self.property_id.selling_price = self.price
        self.property_id.buyer_id=self.partner_id
        self.property_id.state = 'sold'

    def action_refuse(self):
        self.ensure_one()
        if self.status == 'refused':
            return
        self.write({'status': 'refused'})
        self.property_id.selling_price = 0.0
        self.property_id.buyer_id = ''


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"

    name = fields.Char(string="Name", required=True)
    _sql_constraints = [('unique_name', 'unique(name)', 'The name must be unique!')]

    def active_save_tag(self):
        self.ensure_one()
        self.write({
            'name':self.name,
        })


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    name = fields.Char(string="Name", required=True)
    property_ids=fields.One2many('estate.property','property_type_id',string='Properties')
    _sql_constraints = [('unique_name', 'unique(name)', 'The name must be unique!')]


    def active_save_type(self):
        self.ensure_one()
        self.write({
            'name':self.name,
        })


class EstateProperty(models.Model):
    _name = "estate.property"
    _description='Property'

    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)
    name = fields.Char(string="Title", required=True)
    date_availability = fields.Date(string="Availability Date",
                                    default=lambda self: datetime.today() + timedelta(days=90),copy=False)
    postcode = fields.Char(string="Postcode")
    expected_price = fields.Float(string="Expected Price", required=True)
    garage = fields.Boolean(string="Garage")
    selling_price = fields.Float(string="Selling Price",readonly=True)
    garden = fields.Boolean(string="Garden",compute='_compute_onchange', store=True, readonly=False)
    bedrooms = fields.Integer(string="Bedrooms",default=2)
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
    state=fields.Selection(string='Status',copy=False,default="new",
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
    buyer_id = fields.Many2one('res.partner', string="Buyer",readonly=True)
    seller_id = fields.Many2one('res.partner', string="Salesman", index=True, readonly=True, default=lambda self: self.env.user.partner_id.id)
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    total_area=fields.Float(compute='_compute_area_total',store=True)
    amount=fields.Float()
    best_offer = fields.Float(string='Best Offer', compute='_compute_best_offer', store=True)

    @api.depends('living_area','garden_area')
    def _compute_area_total(self):
        for record in self:
            record.total_area=record.living_area+record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for property in self:
            if property.offer_ids:
                property.best_offer = max(property.offer_ids.mapped('price'))
                if property.best_offer<=0:
                    property.best_offer=0.0
                    raise UserError('The price must be strictly positive!')
            else:
                property.best_offer = 0.0

    @api.onchange("garden")
    def _compute_onchange(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 10
        else:
            self.garden_orientation = False
            self.garden_area = False

    def action_save(self):
        self.ensure_one()
        if self.expected_price<1:
            raise UserError('The expected price must be strictly positive!')
        if self.selling_price<0:
            raise UserError('The selling price must be strictly positive!')
        self.write({
            'name': self.name,
            'last_seen': self.last_seen,
            'date_availability': self.date_availability,
            'postcode': self.postcode,
            'expected_price': self.expected_price,
            'garage': self.garage,
            'selling_price': self.selling_price,
            'garden': self.garden,
            'bedrooms': self.bedrooms,
            'active': self.active,
            'living_area': self.living_area,
            'garden_orientation': self.garden_orientation,
            'facades': self.facades,
            'state': self.state,
            'garden_area': self.garden_area,
            'description': self.description,
            'property_type_id': self.property_type_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'tag_ids': self.tag_ids,
            'offer_ids': self.offer_ids,
            'total_area': self.total_area,
            'amount': self.amount,
            'best_offer': self.best_offer
        })

    def action_sold_(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError('Canceled properties cannot be set as sold.')
            record.state = 'sold'

    def action_canceled_(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Sold properties cannot be canceled.')
            record.state = 'canceled'
