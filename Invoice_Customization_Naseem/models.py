# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.osv import osv
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
import datetime
from datetime import datetime,date,timedelta,time
import dateutil.parser
from dateutil.relativedelta import relativedelta

from itertools import groupby

import collections
from collections import namedtuple
import json
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError

class account_bank_extention(models.Model):
	_inherit = 'account.bank.statement.line'

	received_by 	= fields.Char(string="Received By")
	delivered_by 	= fields.Char(string="Delivered By") 
	bilty_no 		= fields.Char(string="Bilty No.") 
	origin 			= fields.Char(string="Source Document") 
	warehouse_id 	= fields.Char(string="WareHouse ID") 

class stock_picking_own(models.Model):
	_inherit 	= 'stock.picking'
	backorder 		= fields.Boolean(string="Back Order", invisible=True)
	bilty_no  		= fields.Char(string="Billty No.")
	print_do 		= fields.Boolean(string="Print DO", default=True) 
	# bilty_recieved  = fields.Float(string="Billty Expense Received")
	packing_expense = fields.Float(string="Packing Expense")
	bilty_paid 		= fields.Float(string="Billty Amount")
	received_by 	= fields.Char(string="Received by")
	transporter 	= fields.Many2one('res.partner',string="Transporter")

	reference_no 	= fields.Char(string="Reference No.")
	carton_no		= fields.Char(string="No. of Carton")
	bundle_no		= fields.Char(string="No. of Bundles")
	delivered_by	= fields.Char(string="Delivered By")
	warehouse 		= fields.Many2one('account.bank.statement',string="Cash Account")

	state = fields.Selection([
		('draft', 'Draft'),
		('cancel', 'Cancelled'),
		('waiting', 'Waiting Another Operation'),
		('confirmed', 'Waiting Availability'),
		('partially_available', 'Partially Available'),
		('assigned', 'Available'),
		('done', 'Done'),
		('close', 'Closed'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


	@api.multi
	def submitt_bilty(self):
		
		cash_enteries = self.env['account.bank.statement'].search([('name','=',self.warehouse.name)])
		cash_entries_lines = self.env['account.bank.statement.line'].search([])
		
		updated = False
		for x in cash_enteries.line_ids:
			if self.name == x.warehouse_id:
				x.date 			= self.min_date
				x.name 			= self.reference_no
				x.partner_id 	= self.partner_id.id
				x.ref 			= self.reference_no
				x.received_by 	= self.received_by
				x.delivered_by 	= self.delivered_by
				x.bilty_no 		= self.bilty_no
				x.origin 		= self.origin
				x.warehouse_id 	= self.name
				x.amount 		= self.bilty_paid + self.packing_expense
				
				updated = True

		if updated == False:
			create_lines = cash_entries_lines.create({
				'date':self.min_date,
				'name':self.reference_no,
				'partner_id':self.partner_id.id, 
				'ref':self.reference_no,
				'amount':self.bilty_paid + self.packing_expense,
				'received_by':self.received_by,
				'delivered_by':self.delivered_by,
				'bilty_no':self.bilty_no ,
				'origin':self.origin,
				'warehouse_id':self.name,
				'statement_id':cash_enteries.id
				})

		return True



	def do_new_transfer(self):
		new_record = super(stock_picking_own, self).do_new_transfer()

		sale_order = self.env['sale.order'].search([('name','=',self.origin)])
		purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
		
		invoice = self.env['account.invoice'].search([])
		invoice_lines = self.env['account.invoice.line'].search([])
		
		if sale_order:
			create_invoice = invoice.create({
				'journal_id': sale_order.journal.id,
				'partner_id':sale_order.partner_id.id,
				'transporter':sale_order.transporter.id,
				'remaining_payment_days':sale_order.remaining_payment_days,
				'due' : sale_order.due,
				'user_id' : sale_order.user_id.id,
				'payment_term_id' : sale_order.payment_term_id.id,
				'due_days' : sale_order.due_days,
				'date_invoice' : sale_order.date_order,
				'incoterm' : sale_order.incoterm.id,
				})

			for x in sale_order.order_line:
				for y in self.pack_operation_product_ids:
					if x.product_id.id == y.product_id.id:
						if x.product_id.property_account_income_id.id:
							account_id = x.product_id.property_account_income_id.id
						else:
							account_id = x.product_id.categ_id.property_account_income_categ_id	
						create_invoice_lines= invoice_lines.create({
							'product_id':x.product_id.id,
							'uom':x.uom,
							'quantity': y.qty_done,
							'carton': y.qty_done/x.product_id.pcs_per_carton,
							'last_sale': x.last_sale,
							'price': x.price.id,
							'price_unit': x.price_unit,
							'discount': x.discount,
							'customer_price': x.customer_price,
							'price_subtotal': x.price_subtotal,
							'promo_code': x.promo_code,
							'account_id': account_id.id,
							'name' : x.name,
							'invoice_id' : create_invoice.id
							})
		if purchase_order:
			create_invoice = invoice.create({
				'journal_id': 3,
				'partner_id':purchase_order.partner_id.id,
				'transporter':purchase_order.transporter.id,
				# 'remaining_payment_days':purchase_order.remaining_payment_days,
				# 'due' : purchase_order.due,
				# 'user_id' : purchase_order.user_id.id,
				'payment_term_id' : purchase_order.payment_term_method.id,
				# 'due_days' : purchase_order.due_days,
				'date_invoice' : purchase_order.date_order,
				'incoterm' : purchase_order.incoterm.id,
				'type':"in_invoice",
				})

			for x in purchase_order.order_line:
				for y in self.pack_operation_product_ids:
					if x.product_id.id == y.product_id.id:
						if x.product_id.property_account_income_id.id:
							account_id = x.product_id.property_account_income_id.id
						else:
							account_id = x.product_id.categ_id.property_account_income_categ_id	
						create_invoice_lines= invoice_lines.create({
							'product_id':x.product_id.id,
							# 'uom':x.uom,
							'quantity': y.qty_done,
							'carton': y.qty_done/x.product_id.pcs_per_carton,
							# 'last_sale': x.last_sale,
							# 'price': x.price.id,
							'price_unit': x.price_unit,
							# 'discount': x.discount,
							# 'customer_price': x.customer_price,
							'price_subtotal': x.price_subtotal,
							# 'promo_code': x.promo_code,
							'account_id': 3,
							'name' : x.name,
							'invoice_id' : create_invoice.id
							})
	
		return new_record

	@api.multi
	def _create_backorder(self, backorder_moves=[]):
		""" Move all non-done lines into a new backorder picking. If the key 'do_only_split' is given in the context, then move all lines not in context.get('split', []) instead of all non-done lines.
		"""
		# TDE note: o2o conversion, todo multi

		backorders = self.env['stock.picking']
		for picking in self:
			backorder_moves = backorder_moves or picking.move_lines
			if self._context.get('do_only_split'):
				not_done_bo_moves = backorder_moves.filtered(lambda move: move.id not in self._context.get('split', []))
			else:
				not_done_bo_moves = backorder_moves.filtered(lambda move: move.state not in ('done', 'cancel'))
			if not not_done_bo_moves:
				continue
			backorder_picking = picking.copy({
				'name': '/',
				'move_lines': [],
				'pack_operation_ids': [],
				'backorder_id': picking.id,
				'backorder':True,
			})
			picking.message_post(body=_("Back order <em>%s</em> <b>created</b>.") % (backorder_picking.name))
			not_done_bo_moves.write({'picking_id': backorder_picking.id})
			if not picking.date_done:
				picking.write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
			backorder_picking.action_confirm()
			backorder_picking.action_assign()
			backorders |= backorder_picking



		purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
		sale_order = self.env['sale.order'].search([('name','=',self.origin)])
		if purchase_order:
			purchase_order.state = "partial"
		if sale_order:
			sale_order.state= "partial"

		return backorders




class stock_pack_extension(models.Model):
	_inherit 	= 'stock.pack.operation'

	carton_to 	= fields.Float(string="Carton To Do")
	carton_done = fields.Float(string="Carton Done")

	@api.onchange('product_qty')
	def calculate_cartons_to(self):
		if self.product_qty:
			self.carton_to = self.product_qty / self.product_id.pcs_per_carton
			# self.qty_done = self.product_id.pcs_per_carton * self.product_qty
			# self.carton_done = self.qty_done / self.product_id.pcs_per_carton 

	@api.onchange('carton_done')
	def calculate_cartons_done(self):
		if self.carton_done:
			self.qty_done = self.product_id.pcs_per_carton * self.carton_done

	@api.onchange('qty_done')
	def calculate_qty_done(self):
		if self.qty_done:
			self.carton_done =  self.qty_done / self.product_id.pcs_per_carton


class sale_order_customized(models.Model):
	_inherit = 'sale.order'

	due_days 				= fields.Integer(string="Due Days", compute="compute_remaining_days")
	due 					= fields.Char(string="Due")
	transporter 			= fields.Many2one('res.partner',string="Transporter")
	remaining_payment_days  = fields.Datetime(string="Remaining Payment Days")
	direct_invoice_check 	= fields.Boolean(string="Direct Invoice", readonly="1")
	journal 				= fields.Many2one('account.journal', string="Journal")
	# state = fields.Selection(selection_add=[('confirm', 'Confirm'),('drft', 'Draft')])
	state2 = fields.Selection([
	('draft', 'Draft'),
	('confirm', 'Confirm'),
	('partial', 'Partial'),
	('complete', 'Complete'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
	
	state = fields.Selection([
	('draft', 'Quotation'),
	('sent', 'Quotation Sent'),
	('sale', 'Sales Order'),
	('done', 'Locked'),
	('cancel', 'Cancelled'),
	('partial', 'Partial'),
	('complete', 'Complete'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


	@api.multi
	def make_delivery(self):
		sale_deliveries = self.env['stock.picking'].search([('origin','=',self.name),('backorder','=',True)])
		if sale_deliveries:
			sale_deliveries.backorder = False
		else:
			raise ValidationError('No Pending Delivery Exists for this Sale Order')




	@api.multi
	def complete_order(self):
		if self.direct_invoice_check == True:
			self.state2 = "complete"
		else:
			self.state = "complete"
		back_order = self.env['stock.picking'].search([('origin','=',self.name),('state','not in',('done','cancel'))])
		if back_order:
			print "Found"
			print "xxxxXXXxxxXXXXxxxxxxxxxxx"
			back_order.state = "cancel"


	@api.multi
	def generate_wizard(self):
		return {
		'type': 'ir.actions.act_window',
		'name': 'Add Products',
		'res_model': 'wizard.class',
		'view_type': 'form',
		'view_mode': 'form',
		'target' : 'new',
		}

	# incoterm = fields.Many2one('stock.incoterms')
	due = fields.Char()
###################################################
	instant_promo = fields.One2many('instant.promo.so','instant_promo_id')

	@api.one
	def compute_remaining_days(self):
		current_date = fields.Datetime.now()
		if self.date_order and self.payment_term_id and self.remaining_payment_days:
			fmt = '%Y-%m-%d %H:%M:%S'
			d1 = datetime.strptime(current_date, fmt)
			d2 = datetime.strptime(self.remaining_payment_days, fmt)
			self.due_days = str((d1-d2).days)

	@api.onchange('partner_id')
	def select_journal(self):
		journal_env_cash = self.env['account.journal'].search([('type','=',"cash")])
		journal_env_sale = self.env['account.journal'].search([('type','=',"sale")])

		if self.partner_id:	
			if self.direct_invoice_check == True:
				self.journal = journal_env_cash.id
			else:
				self.journal = journal_env_sale.id

			self.transporter = self.partner_id.transporter
			self.payment_term_id = self.partner_id.payment_term
			self.incoterm = self.partner_id.incoterm
			self.currency_id = self.partner_id.currency






	@api.onchange('payment_term_id','date_order')
	def count_total(self):
		if self.date_order and self.payment_term_id:
			date_start_dt = fields.Datetime.from_string(self.date_order)
			dt 	= date_start_dt + relativedelta(days=self.payment_term_id.line_ids.days)
			self.remaining_payment_days = fields.Datetime.to_string(dt)
			fmt = '%Y-%m-%d %H:%M:%S'
			d1 = datetime.strptime(self.date_order, fmt)
			d2 = datetime.strptime(self.remaining_payment_days, fmt)
			self.due_days = str((d1-d2).days)

	@api.multi
	def validate_direct_invoice(self):
		# self.state = 'done'

#####################################
#  Create Customer Invoice  
#####################################

		sale_order = self.env['sale.order'].search([('partner_id','=',self.partner_id.id),(('state','=',"sale"))])
		total = 0 
		for x in sale_order:
			total = total + x.amount_total


		invoice = self.env['account.invoice'].search([])
		invoice_lines = self.env['account.invoice.line'].search([])
		create_invoice = invoice.create({
			'journal_id': self.journal.id,
			'partner_id':self.partner_id.id,
			'transporter':self.transporter.id,
			'remaining_payment_days':self.remaining_payment_days,
			'due' : self.due,
			'user_id' : self.user_id.id,
			'payment_term_id' : self.payment_term_id.id,
			'due_days' : self.due_days,
			'date_invoice' : self.date_order,
			'incoterm' : self.incoterm.id,
			'balance' : total,
			'state2' : "confirm"
			})

		for x in self.order_line:
			if x.product_id.property_account_income_id.id:
				account_id = x.product_id.property_account_income_id.id
			else:
				account_id = x.product_id.categ_id.property_account_income_categ_id.id	
			create_invoice_lines= invoice_lines.create({
				'product_id':x.product_id.id,
				'uom':x.uom,
				'quantity': x.product_uom_qty,
				'carton': x.carton,
				'last_sale': x.last_sale,
				'price': x.price.id,
				'price_unit': x.price_unit,
				'discount': x.discount,
				'customer_price': x.customer_price,
				'price_subtotal': x.price_subtotal,
				'promo_code': x.promo_code,
				'account_id': account_id,
				'name' : x.name,
				'invoice_id' : create_invoice.id
				})	
	#####################################
	#  Create Stock Entry 
	#####################################

		inventory = self.env['stock.picking']
		inventory_lines = self.env['stock.move'].search([])
		create_inventory = inventory.create({
			'partner_id':self.partner_id.id,
			'location_id':15,
			'picking_type_id' : 4,
			'location_dest_id' : 9,

			})
		for x in self.order_line:
			create_inventory_lines= inventory_lines.create({
				'product_id':x.product_id.id,
				'product_uom_qty':x.product_uom_qty,
				'product_uom': x.product_id.uom_id.id,
				'location_id':15,
				'picking_id': create_inventory.id,
				'name':"test",
				'location_dest_id': 9,
				})	
	#####################################
	#  Create Journal Entry 
	#####################################
		journal_entries = self.env['account.move'].search([('promo_id','=',self.id)])
		journal_entries_lines = self.env['account.move.line'].search([])
		if not journal_entries:
			create_journal_entry = journal_entries.create({
				'journal_id': self.journal.id,
				'date':self.date_order,
				'promo_id':self.id,
				# 'ref':active_class.order_no,
				})
			
			create_debit = journal_entries_lines.create({
				'account_id':1,
				'partner_id':self.partner_id.id,
				'name':"test",
				'debit':self.amount_total,
				'move_id':create_journal_entry.id
				})
			create_credit = journal_entries_lines.create({
				'account_id':3,
				'partner_id':self.partner_id.id,
				'name':"test",
				'credit':self.amount_total,
				'move_id':create_journal_entry.id
				})

		else:
			for x in journal_entries.line_ids:
				if x.debit ==0:
					x.credit=self.amount_total

				if x.credit ==0:
					x.debit=self.amount_total

	# @api.multi
	# def validate_sale_order(self):
	# 	invoice = self.env['account.invoice'].search([])
	# 	invoice_lines = self.env['account.invoice.line'].search([])
	# 	create_invoice = invoice.create({
	# 		'journal_id': self.journal.id,
	# 		'partner_id':self.partner_id.id,
	# 		'transporter':self.transporter.id,
	# 		'remaining_payment_days':self.remaining_payment_days,
	# 		'due' : self.due,
	# 		'user_id' : self.user_id.id,
	# 		'payment_term_id' : self.payment_term_id.id,
	# 		'due_days' : self.due_days,
	# 		'date_invoice' : self.date_order,
	# 		'incoterm' : self.incoterm.id,
	# 		})

	# 	for x in self.order_line:
	# 		if x.product_id.property_account_income_id.id:
	# 			account_id = x.product_id.property_account_income_id.id
	# 		else:
	# 			account_id = x.product_id.categ_id.property_account_income_categ_id	
	# 		create_invoice_lines= invoice_lines.create({
	# 			'product_id':x.product_id.id,
	# 			'uom':x.uom,
	# 			'quantity': x.product_uom_qty,
	# 			'carton': x.carton,
	# 			'last_sale': x.last_sale,
	# 			'price': x.price.id,
	# 			'price_unit': x.price_unit,
	# 			'discount': x.discount,
	# 			'customer_price': x.customer_price,
	# 			'price_subtotal': x.price_subtotal,
	# 			'promo_code': x.promo_code,
	# 			'account_id': account_id.id,
	# 			'name' : x.name,
	# 			'invoice_id' : create_invoice.id
	# 			})					

	@api.model
	def create(self, vals):	
		new_record = super(sale_order_customized, self).create(vals)
		self.delete_zero_products()
		return new_record

	# @api.model
	# def create(self, vals):	
	# 	new_record = super(sale_order_customized, self).create(vals)
	# 	self.delete_zero_products()
	# 	return new_record

	@api.multi
	def write(self, vals):
		super(sale_order_customized, self).write(vals)
		self.delete_zero_products()
		return True
	def delete_zero_products(self):
		for lines in self.instant_promo:
			if lines.qty == 0:
				lines.unlink()

	@api.onchange('partner_id')
	def get_due_ammount(self):
		all_records = self.env['account.invoice'].search([('state','=',"open")])
		total_30  = 0
		total_60  = 0
		total_90  = 0
		total_120 = 0
		if self.partner_id:
			for x in all_records:
				if x.partner_id == self.partner_id:
					if x.due_days <=30:
						total_30 = total_30 + x.amount_total
					elif x.due_days <=60:
						total_60 = total_60 + x.amount_total
					elif x.due_days <=90:
						total_90 = total_90 + x.amount_total	
					else:
						total_120 = total_120 + x.amount_total	
			self.due = str(total_30) + "  (30 Days)       " + str(total_60) + "  (60 Days)       " +  str(total_90) + "  (90 Days)      " + str(total_120) + "  (120 Days)   " 

	@api.multi
	def action_confirm(self):
		for lines in self.instant_promo:
			self.order_line.create({
				'product_id': lines.product_id.id,
				'product_uom_qty':lines.qty,
				'price_unit': 0,
				'order_id':self.id
				})
		return  super(sale_order_customized,self).action_confirm()

	@api.constrains('order_line')
	def check_product_repeatetion(self):
		items= []
		flag = 0
		if self.product_id:
			for x in self.order_line:
				items.append(x.product_id.id)
		counter=collections.Counter(items)
		for x in counter.values():
			if x > 1:
				flag = 1
		if flag == 1:
			raise ValidationError('Same Product exists multiple times in Sale Order')

	@api.onchange('order_line')
	def on_change_instant_promo(self):
		
		items= []
		flag = 0
		if self.product_id:
			for x in self.order_line:
				items.append(x.product_id.id)
		counter=collections.Counter(items)
		for x in counter.values():
			if x > 1:
				flag = 1
		if flag == 1:
			raise ValidationError('Same Product exists multiple times in Sale Order')
		else:
			instant_promo_lines = self.env['promo.instant'].search([('sales_promo_id5.scheme_from_dt','<',self.date_order), ('sales_promo_id5.scheme_to_dt','>',self.date_order), ('sales_promo_id5.stages','=',"validate")])
			sale_order_lines = self.env['sale.order.line'].search([])

			for x in self.order_line:
				for y in instant_promo_lines:
					if x.product_id.id == y.product.id and x.order_id.partner_id in y.sales_promo_id5.customer:
						invoice_lines = self.env['account.invoice.line'].search([('invoice_id.date','>',y.sales_promo_id5.scheme_from_dt), ('invoice_id.date','<',y.sales_promo_id5.scheme_to_dt),('product_id.id','=',y.product.id),('invoice_id.partner_id.id','=',self.partner_id.id),('invoice_id.state','!=',"draft")])
						current_quantity = 0
						for qt in self.order_line:
							if qt.product_id.id == y.product.id and qt.price_unit != 0:
								current_quantity = current_quantity + qt.product_uom_qty
						invoice_total = (self.quantity(invoice_lines)[0] - self.quantity(invoice_lines)[2]) + current_quantity
						invoice_total_promo =  self.quantity(invoice_lines)[1] - self.quantity(invoice_lines)[3]
						reward_quantity = (int(invoice_total/y.qty) * y.qty_reward) - invoice_total_promo  
						
						ids = []
						for a in self.instant_promo:
							ids.append(a.product_id.id)
						if x.product_id.id not in ids and reward_quantity > 0:
							self.instant_promo |= self.instant_promo.new({'product_id':x.product_id.id,'qty': reward_quantity,'instant_promo_id': self.id,})
						elif x.product_id.id in ids:
							for c in self.instant_promo:
								if c.product_id.id == x.product_id.id:
									c.qty = reward_quantity

			product_lst = []
			for y in self.order_line:
				product_lst.append(y.product_id.id)
			for lines in self.instant_promo:
				if lines.product_id.id not in product_lst:
					lines.qty = 0
		for x in self.order_line:
			x.carton = x.product_uom_qty / x.product_id.pcs_per_carton
				
	
	def quantity(self,invoice):
		total_quantity = [0,0,0,0]
		for z in invoice:
			if z.invoice_id.type == "out_invoice":
				if z.price_unit != 0:
					total_quantity[0] = total_quantity[0] + z.quantity
				else:
					total_quantity[1] = total_quantity[1] + z.quantity
			elif z.invoice_id.type == "out_refund":
				if z.price_unit != 0:
					total_quantity[2] = total_quantity[2] + z.quantity
				else:
					total_quantity[3] = total_quantity[3] + z.quantity
		return total_quantity


class instant_promo_so(models.Model):
	_name = 'instant.promo.so'

	product_id = fields.Many2one('product.product', string = "Product")
	qty        = fields.Float(string = "Quantity")

	instant_promo_id = fields.Many2one('sale.order')


class sale_order_line_extension(models.Model):
	_inherit = "sale.order.line"

	uom 			= fields.Char(string="UOM")
	carton 			= fields.Float(string="Quantity (CARTONS)")
	last_sale 		= fields.Float(string="Last Sale")  
	promo_code 		= fields.Char(string="PROMO CODE")
	customer_price 	= fields.Float(string="Net Price")
	pricelist_ext 	= fields.Many2one('product.pricelist', string = "Pricelist")
	price 			= fields.Many2one('product.pricelist.item')
	check_boolean 	= fields.Boolean()
	set_list_price 	= fields.Boolean()
	check_promo 	= fields.Boolean(string="Promo ?", default=False)
	


	@api.onchange('product_id')
	def check_pricelist_lastSale_Promo(self):
########################################
#       checking Pricelist
########################################
		if self.product_id:
			self.price_unit = self.product_id.list_price_own
			self.uom = self.product_id.uom
			pricelist = self.env['product.pricelist'].search([('id','=',self.order_id.partner_id.linked_pricelist.id)])
			pricelist_lines = self.env['product.pricelist.item'].search([('pricelist_id','=',pricelist.id)])
			promoList = self.env['promo.customer'].search([('customer','=',self.order_id.partner_id.id),('stages','=',"confirm")])
			promoWizard = self.env['naseem.sales.promo'].search([])
			
			for x in pricelist_lines:
				if x.product_id.id == self.product_id.id or x.categ_id.id == self.product_id.categ_id.id:
					self.pricelist_ext = self.order_id.partner_id.linked_pricelist.id
					self.check_boolean = True

			for x in promoList:
				if x.promotion.applicable_on == "product": 
					if x.promotion.scheme_application == "list_price" and x.promotion.prod_name == self.product_id :
						self.set_list_price = True
						self.pricelist_ext = 2 
					else:
						self.set_list_price = False
				elif x.promotion.applicable_on == "category":
					if x.promotion.scheme_application == "list_price" and x.promotion.prod_cat == self.product_id.categ_id:
						self.set_list_price = True
						self.pricelist_ext = 2 
					else:
						self.set_list_price = False
		all_records = self.env['account.invoice'].search([])
		all_promotions = self.env['naseem.sales.promo'].search([])

########################################
#       Checking Invoice
########################################

		for a in all_promotions:
			if self.product_id == a.prod_name:
				self.promo_code = a.scheme_no
				self.check_promo = True
			else:
				self.promo_code = " "
				self.check_promo = False

########################################
#       Last Sale Price
########################################

		for x in all_records:
			if self.order_id.partner_id == x.partner_id:	
				for y  in x.invoice_line_ids:
					if self.product_id == y.product_id:
						self.last_sale = y.customer_price
						return

	@api.onchange('discount','price_unit')
	def calculate_customer_price(self):
		discounted_amount = (self.price_unit/100)*self.discount
		self.customer_price = self.price_unit - discounted_amount

	@api.onchange('product_uom_qty')
	def get_cartons(self):
		if self.product_uom_qty and self.product_id:
			self.carton = self.product_uom_qty / self.product_id.pcs_per_carton

	@api.onchange('carton')
	def get_quantity(self):
		if self.carton and self.product_id:
			self.product_uom_qty = self.carton * self.product_id.pcs_per_carton

	@api.onchange('price')
	def get_price(self):
	   self.pricelist_ext = self.price.pricelist_id.id

	@api.multi
	def _get_display_price(self, product):
	   if self.order_id.pricelist_id.discount_policy == 'without_discount':
		  from_currency = self.order_id.company_id.currency_id
		  return from_currency.compute(product.lst_price, self.pricelist_ext.currency_id)
	   return product.with_context(pricelist=self.pricelist_ext.id).price

	@api.multi
	@api.onchange('product_id','pricelist_ext')
	def product_id_change(self):
		if not self.product_id:
			return {'domain': {'product_uom': []}}

		vals = {}
		domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
		if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
			vals['product_uom'] = self.product_id.uom_id
			vals['product_uom_qty'] = 1.0

		product = self.product_id.with_context(
			lang=self.order_id.partner_id.lang,
			partner=self.order_id.partner_id.id,
			quantity=vals.get('product_uom_qty') or self.product_uom_qty,
			date=self.order_id.date_order,
			pricelist=self.pricelist_ext.id,
			uom=self.product_uom.id
			)
		name = product.name_get()[0][1]
		if product.description_sale:
			name += '\n' + product.description_sale
		vals['name'] = name

		self._compute_tax_id()

		if self.pricelist_ext and self.order_id.partner_id:
			vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
		self.update(vals)

		title = False
		message = False
		warning = {}
		if product.sale_line_warn != 'no-message':
			title = _("Warning for %s") % product.name
			message = product.sale_line_warn_msg
			warning['title'] = title
			warning['message'] = message
			if product.sale_line_warn == 'block':
				self.product_id = False
			return {'warning': warning}
		return {'domain': domain}
	


class sale_invoice_customized(models.Model):
	_inherit = 'account.invoice'

	due_days = fields.Integer(string="Due Days")
	due = fields.Char(string="Due")
	transporter = fields.Many2one('res.partner',string="Transporter")
	incoterm = fields.Many2one('stock.incoterms')
	check_direct_invoice = fields.Boolean('Direct Invoice', default=True)
	remaining_payment_days =fields.Date('Remaining Payment Days')



class sale_invoice_line_extension(models.Model):
	_inherit = "account.invoice.line"

	uom = fields.Char(string="UOM", readonly="1")
	carton = fields.Float(string="Quantity (CARTONS)")
	last_sale = fields.Float(string="Last Sale")  
	promo_code = fields.Char(string="PROMO CODE")
	customer_price = fields.Float(string="Net Price")
	price = fields.Many2one('product.pricelist.item')

