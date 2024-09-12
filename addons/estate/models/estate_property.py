from odoo import fields,models,api
from datetime import datetime, timedelta
from odoo.exceptions import *


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'
    _order = "price desc"

    price = fields.Float(string='Price', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    status = fields.Selection([
        (" "," "),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], string='Status', default=' ')
    property_id = fields.Many2one('estate.property', string='Property')
    validity=fields.Integer(string='Validity',default=7)
    date_deadline=fields.Date(string="Deadline",compute='_compute_deadline',store=True,readonly=False)
    property_type_id = fields.Many2one('estate.property.type',string='Property Type', related='property_id.property_type_id', store=True)

    @api.model
    def create(self, vals):
        property_obj = self.env['estate.property'].browse(vals['property_id'])
        if vals.get('price', 0) < property_obj.expected_price:
            raise UserError(f'The offer must be higher than {property_obj.expected_price}')
        return super(EstatePropertyOffer, self).create(vals)

    @api.depends('validity')
    def _compute_deadline(self):
        for deadline in self:
            deadline.date_deadline=datetime.today() + timedelta(days=deadline.validity)


    def action_accept(self):
        self.ensure_one()
        if self.price < 0:
            raise UserError('The expected price must be strictly positive!')
        if self.property_id.state == 'canceled':
            raise UserError('Canceled properties cannot be accepted.')
        self.write({'status': 'accepted'})
        other_offers = self.search([
            ('property_id', '=', self.property_id.id),
            ('id', '!=', self.id)
        ])
        other_offers.write({'status': 'refused'})
        self.property_id.selling_price = self.price
        self.property_id.buyer_id=self.partner_id
        self.property_id.state = 'offer accepted'

    def action_refuse(self):
        self.ensure_one()
        if self.property_id.state == 'canceled':
            raise UserError('Canceled properties cannot be refused.')
        self.write({'status': 'refused'})
        self.property_id.selling_price = 0.0
        self.property_id.buyer_id = ''
        self.property_id.state='offer received'


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    _sql_constraints = [('unique_name', 'unique(name)', 'The name must be unique!')]
    color = fields.Integer(string="Color")


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    _sql_constraints = [('unique_name', 'unique(name)', 'The name must be unique!')]
    property_ids=fields.One2many('estate.property','property_type_id',string='Properties')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers', readonly=True)
    offer_count = fields.Integer(string='Offers Count', compute='_compute_offer_count')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    def action_view_offers(self):
        return {
            'name': 'Offers',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.property.offer',
            'view_mode': 'tree,form',
            'domain': [('property_type_id', '=', self.id)],
        }

class EstateProperty(models.Model):
    _name = "estate.property"
    _description='Property'
    _order = "id desc"


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
    state=fields.Selection(string='Status',readonly=True,copy=False,default="new",
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
    new_seller_id=fields.Many2one('res.users', string="Salesman", index=True, readonly=True, default=lambda self: self.env.user.partner_id.id)
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    total_area=fields.Float(compute='_compute_area_total',store=True)
    amount=fields.Float()
    best_offer = fields.Float(string='Best Offer', compute='_compute_best_offer', store=True)
    sequence = fields.Integer('Sequence', default=1)

    @api.ondelete(at_uninstall=False)
    def _compute_delete(self):
        if self.state!='new' and self.state!='canceled':
            raise UserError('Only new and canceled properties can be deleted!')

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
            if len(property.offer_ids)>0:
                property.state = 'offer received'

    @api.onchange("garden")
    def _compute_onchange(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 10
        else:
            self.garden_orientation = False
            self.garden_area = False


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
            record.selling_price=0.0
