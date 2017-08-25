# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError

# Adding Contacts and Adresses in Customer Form

# class addrerss_extension(models.Model): 
#     _inherit = 'res.partner'

#     name            = fields.Char(string="Customer Name")
#     dob             = fields.Date()
#     stop_invoice    = fields.Boolean(string = "Stop Saving Invoice When Credit Limit Exceed")
#     credit_limit    = fields.Float(string="Credit Limit")
#     contact_address = fields.One2many('address.contacts','address_contact_id')
#     check_trans     = fields.Boolean(string="Is Transporter")
#     transporter		= fields.Many2one('res.partner',string="Transporter")
#     payment_term	= fields.Many2one('account.payment.term',string="Payment Term")
#     incoterm	 	= fields.Many2one('stock.incoterms',string="Delivery Terms")

