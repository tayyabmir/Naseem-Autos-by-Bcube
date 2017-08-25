# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError

# Adding Contacts and Adresses in Customer Form

class addrerss_extension(models.Model): 
    _inherit = 'res.partner'

    name            = fields.Char(string="Customer Name")
    dob             = fields.Date()
    stop_invoice    = fields.Boolean(string = "Stop Saving Invoice When Credit Limit Exceed")
    credit_limit    = fields.Float(string="Credit Limit")
    contact_address = fields.One2many('address.contacts','address_contact_id')
    check_trans     = fields.Boolean(string="Is Transporter")
    transporter     = fields.Many2one('res.partner',string="Transporter")
    forwarder		= fields.Many2one('res.partner',string="Forwarder")
    payment_term	= fields.Many2one('account.payment.term',string="Payment Term")
    incoterm	 	= fields.Many2one('stock.incoterms',string="Delivery Terms")
    check_purchase  = fields.Boolean(string="Vendor")
    clearing_agent  = fields.Many2one('res.partner',string="Clearing Agent")
    check_forwarder = fields.Boolean(string="Forwarder")
    check_clearing_agent = fields.Boolean(string="Clearing Agent Check")
    check_supplier       = fields.Boolean(string="Check Supplier")
    terms_conditions     = fields.Text(string="Terms and Conditions")
    contact_person       = fields.Char(string="Contact Person")
    currency             = fields.Many2one('res.currency',string="Currency")


class res_partner_bank_extension(models.Model):
    _inherit = 'res.partner.bank'

    ac_title = fields.Char(string="Account Title")
    branch_code = fields.Char(string="Brach Code")

# class vendors_details(models.Model):
#     _name = 'ved.details'


#     name    = fields.Char(string="Name")
#     adress  = fields.Char(string="Adress")
#     title   = fields.Char(string="Title")
#     dob     = fields.Char(string="DOB")
#     phone   = fields.Char(string="Phone")
#     mobile  = fields.Char(string="Mobile")
#     fax     = fields.Char(string="Fax")
#     email   = fields.Char(string="Email")