# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta



class naseem_sales_promo(models.Model):
	_name 			= 'naseem.sales.promo'
	_rec_name       = 'scheme_no'
#Sales Promotion Top Header
	active 				    = fields.Boolean(default = 1)
	intimation_date 		= fields.Date(string="Intimation Date")
	scheme_no 				= fields.Char(string='Scheme No', index=True, readonly=True)
	scheme_from_dt			= fields.Date('From Date', required = "True")
	scheme_to_dt			= fields.Date('To Date', required = "True")
	prod_cat				= fields.Many2one('product.category', string = 'Category')
	prod_name				= fields.Many2one('product.product', string ='Product')
	scheme_type 			= fields.Selection([('percentage_disc', 'Percentage Wise Discount'),
											('product_scheme','Product Against Promotional Scheme'),
											('points_scheme','Point Base Scheme'),
											('instant_promo','Instant Promo')
											],string = "Scheme Type") #discount type % or any other type of discount
	scheme       			= fields.Selection([('value', 'Value Wise'),
											('qty','Quantity Wise')
											],string = "Scheme")
	# scheme_uom       		= fields.Selection([('pieces','In Pieces'),
	# 										('cartons','In Cartons')
	# 										],string = "Scheme UOM") 
	# scheme_days				= fields.Char('Intimation') #Promo Period e.g. 60 days
	scheme_application		= fields.Selection([('over','Over & Above'),
											('list_price','List Price'),
											],string = "Scheme Application")  # Over and above or on List Price
	applicable_on		    = fields.Selection([('product','Single Product'),
											('category','Whole Category'),
											],string = "Applicable On")
	# approval_dt	            = fields.Selection([('yes', 'Yes'),('no','No')], 'Approval After Due Date', default='no')
	slabs                   = fields.One2many('promo.slabs','sales_promo_id1')
	prod_gift_base          = fields.One2many('promo.gift','sales_promo_id2')
	points_base		        = fields.One2many('promo.points','sales_promo_id3')
	reward		        	= fields.One2many('promo.rewards','sales_promo_id4')
	instant_promo		    = fields.One2many('promo.instant','sales_promo_id5')
	customer		        = fields.Many2many('res.partner')
	target_qty				= fields.Float(string ='Target')
	points 					= fields.Float(string = 'Points')
	stages                  = fields.Selection([
		('draft', 'Draft'),
		('validate', 'Validate'),
		],string = "Stages", default = 'draft')


	@api.model
	def create(self, vals):
		vals['scheme_no'] = self.env['ir.sequence'].next_by_code('naseem.sales.promo')
		new_record = super(naseem_sales_promo, self).create(vals)
		start_date = new_record.scheme_from_dt
		end_date = new_record.scheme_to_dt
		intimation = new_record.intimation_date
		self._check_total(start_date,end_date,intimation)

		return new_record


	@api.multi
	@api.constrains()
	def _check_total(self,scheme_from_dt,scheme_to_dt,intimation):
		if scheme_from_dt > scheme_to_dt:
			raise ValidationError('Starting Date is greater than Ending Date')
		if intimation > scheme_to_dt:
			raise ValidationError('Intimation Date is greater than Ending Date')

	@api.onchange('applicable_on')
	def check_scheme_type(self):
		if self.applicable_on == 'category':
			self.scheme = 'value'



	@api.multi
	def validate(self):
		self.stages = "validate"



	@api.onchange('prod_name')
	def on_change_prod_name(self):
		self.prod_cat = self.prod_name.categ_id.id




	@api.multi
	def generate_products(self):
		return {
		'type': 'ir.actions.act_window',
		'name': 'generate_products_wizard',
		'res_model': 'generate.products',
		'view_type': 'form',
		'view_mode': 'form',
		'target' : 'new',
		}


#############################################
# Discount Percenatages on Target Quantities
#############################################
class naseem_sales_promo_slabs(models.Model):
	_name 				= 'promo.slabs'
	

	target_name 		= fields.Char(string = 'Target Name')
	from_target			= fields.Float(string ='From: Target Qty')
	to_target			= fields.Float(string = 'To: Target Qty')
	discount_percentage	= fields.Float(string = 'Discount %')
	sales_promo_id1 	= fields.Many2one('naseem.sales.promo')


	@api.one
	@api.constrains('from_target','to_target')
	def _check_total(self):
		if int(self.from_target) > int(self.to_target):
			raise ValidationError('To Target is greater than From Target')

#############################################
# Product/Gift against promotional scheme
#############################################
class naseem_sales_promo_gift(models.Model):
	_name 				= 'promo.gift'
	

	target_name 		= fields.Char(string = 'Target Name')
	from_target			= fields.Float(string ='From: Target Qty')
	to_target			= fields.Float(string = 'To: Target Qty')
	product_gift		= fields.Many2one('product.product',string = 'Product/Gift')
	sales_promo_id2 	= fields.Many2one('naseem.sales.promo')

	@api.one
	@api.constrains('from_target','to_target')
	def _check_total(self):
		if int(self.from_target) > int(self.to_target):
			raise ValidationError('To Target is greater than From Target')


#############################################
# Point based scheme
#############################################
class naseem_sales_promo_points(models.Model):
	_name 				= 'promo.points'
	

	# prod_name 			= fields.Many2one('product.product',string = 'Product Name')
	target_qty			= fields.Float(string ='Target')
	points 				= fields.Float(string = 'Points')
	sales_promo_id3		= fields.Many2one('naseem.sales.promo')

#############################################
#Rewards on Points
#############################################
class naseem_sales_promo_rewards(models.Model):
	_name 				= 'promo.rewards'
	

	points 			= fields.Float(string = 'Points')
	product			= fields.Many2one('product.product',string ='Product')
	qty             = fields.Float(string = 'Qty')
	discount 		= fields.Float(string = 'Discount')
	product_gift    = fields.Many2one('product.product',string ='Gift')
	
	sales_promo_id4 = fields.Many2one('naseem.sales.promo')

#############################################
#Instant Promo
#############################################
class naseem_sales_instant_promo(models.Model):
	_name 				= 'promo.instant'
	

	product			= fields.Many2one('product.product',string ='Product')
	qty             = fields.Float(string = 'Qty')
	qty_reward 		= fields.Float(string = 'Reward Quantity')
	
	sales_promo_id5 = fields.Many2one('naseem.sales.promo')




class naseem_sales_promo_customer(models.Model):
	_name 				= 'promo.customer'
	_rec_name           = 'customer'
	
	stages     = fields.Selection([
		  ('draft', 'Draft'),
		  ('confirm', 'Confirm'),
		  ('validate', 'Validate'),
		  ('cancel', 'Cancel'),
		  ],string = "Stages", default = 'draft')
	customer 			 = fields.Many2one('res.partner',string = 'Customer Name', required = "True")
	promotion 			 = fields.Many2one('naseem.sales.promo',domain = [('stages','=','validate')], required = "True")
	date                 = fields.Date(required = "True")
	pricelist            = fields.Many2one('product.pricelist', required = "True")
	intimation_date 	 = fields.Date(string="Intimation Date", readonly="1")

	target               = fields.Char(readonly = "True")
	discount_percentage  = fields.Float(string = "Discount Percentage", readonly = "True")
	sale_value           = fields.Float(string = "Sale Value" , readonly = "True")
	sale_quantity        = fields.Float(string = "Sale Quantity" , readonly = "True")
	points_earned        = fields.Float(string = "Points Earned" ,readonly = "True")
	points_consumed      = fields.Float(string = "Points Consumed")
	remaining_points     = fields.Float(string = "Remaining Points")
	product_gift         = fields.Many2one('product.product',string = "Gift Product", readonly = "True")

	promo_history        = fields.One2many('promo.history','promo_customer_id', readonly = "True")
	discounted_amount	 = fields.Float(string="Discounted Amount", readonly="True")
	# check_intimation	 = fields.Boolean(compute="compute_date",string="Check Intimation")
	# check_intimation 	 = field
	check 	 = fields.Selection([('color_orange', 'True'),
		('color_red','False')
		],string = "Check Intimation",compute="compute_date")
	# promo_rewards        = fields.One2many('promo.rewards.customer','promo_reward_id')

	@api.one
	def compute_date(self):
		if  str(date.today()) <= self.promotion.scheme_to_dt and str(date.today()) >= self.intimation_date:
			self.check = 'color_orange'
		elif str(date.today()) > self.promotion.scheme_to_dt:
			self.check = 'color_red'


	@api.one
	@api.constrains('customer','promotion')
	def _check_date(self):
		all_cat_ids = self.env['promo.customer'].search([])
		all_promos = []
		all_customers = []
		for x in all_cat_ids:
			if x.id != self.id:
				all_promos.append(x.promotion.id)
				all_customers.append(x.customer.id)
		if x.promotion.id in all_promos and x.customer.id in all_customers:
			raise ValidationError('Promotion for this customer already exists')

	@api.onchange('promotion')
	def get_intimation_date(self):
		if self.promotion:
			self.intimation_date = self.promotion.intimation_date


	# @api.onchange('promo_rewards')
	# def on_change_points_consumption(self):
	# 	total_consumed = 0
	# 	for x in self.promo_rewards:
	# 		if x.availed:
	# 			total_consumed = total_consumed+ (x.points * x.units)

	# 	self.points_consumed = total_consumed
	# 	self.remaining_points = self.points_earned - self.points_consumed

	# @api.onchange('promotion')
	# def on_change_promotion(self):
	# 	self.promo_rewards.unlink()
	# 	for x in self.promotion.reward:
	# 		self.promo_rewards |= self.promo_rewards.new({'points':x.points,'product': x.product.id,'qty': x.qty,'discount': x.discount,'product_gift': x.product_gift.id,'promo_reward_id':self.id})

	@api.multi
	def confirm(self):
		self.stages = "confirm"
	@api.multi
	def validate(self):
		self.stages = "validate"
	@api.multi
	def in_validate(self):
		self.stages = "confirm"
	@api.multi
	def cancel(self):
		self.stages = "cancel"
		journal_entries = self.env['account.move'].search([('promo_id','=',self.id)])
		if journal_entries:
			journal_entries.unlink()
	@api.multi
	def create_entry(self):
		# active_class = self.env['account.move'].browse(self._context.get('active_id'))
		# generate_so_line= active_class.create({
  #           'journal_id':'1',
  #           })
		journal_entries = self.env['account.move'].search([('promo_id','=',self.id)])
		journal_entries_lines = self.env['account.move.line'].search([])
		if not journal_entries:
			create_journal_entry = journal_entries.create({
					'journal_id': 1,
					'date':self.date,
					'promo_id':self.id,
					# 'ref':active_class.order_no,
					})
			create_debit = journal_entries_lines.create({
				'account_id':1,
				'partner_id':self.customer.id,
				'name':"test",
				'debit':self.discount_value,
				'move_id':create_journal_entry.id
				})
			create_credit = journal_entries_lines.create({
				'account_id':3,
				'partner_id':self.customer.id,
				'name':"test",
				'credit':self.discount_value,
				'move_id':create_journal_entry.id
				})
		else:
			for x in journal_entries.line_ids:
				if x.debit ==0:
					x.credit=self.discount_value

				if x.credit ==0:
					x.debit=self.discount_value



	@api.multi
	def update(self):
		invoice_lines = self.env['account.invoice.line'].search([('invoice_id.date','>=',self.promotion.scheme_from_dt), ('invoice_id.date','<=',self.promotion.scheme_to_dt),('product_id.id','=',self.promotion.prod_name.id),('invoice_id.partner_id.id','=',self.customer.id),('invoice_id.state','!=',"draft"),('invoice_id.type','=',"out_invoice")])
		invoice_lines_refund = self.env['account.invoice.line'].search([('invoice_id.date','>=',self.promotion.scheme_from_dt), ('invoice_id.date','<=',self.promotion.scheme_to_dt),('product_id.id','=',self.promotion.prod_name.id),('invoice_id.partner_id.id','=',self.customer.id),('invoice_id.state','!=',"draft"),('invoice_id.type','=',"out_refund")])
		invoice_lines_cat = self.env['account.invoice.line'].search([('invoice_id.date','>=',self.promotion.scheme_from_dt), ('invoice_id.date','<=',self.promotion.scheme_to_dt),('product_id.categ_id.id','=',self.promotion.prod_cat.id),('invoice_id.partner_id.id','=',self.customer.id),('invoice_id.state','!=',"draft"),('invoice_id.type','=',"out_invoice")])
		invoice_lines_refund_cat = self.env['account.invoice.line'].search([('invoice_id.date','>=',self.promotion.scheme_from_dt), ('invoice_id.date','<=',self.promotion.scheme_to_dt),('product_id.categ_id.id','=',self.promotion.prod_cat.id),('invoice_id.partner_id.id','=',self.customer.id),('invoice_id.state','!=',"draft"),('invoice_id.type','=',"out_refund")])
		promo_history_tree = self.env['promo.history'].search([('promo_customer_id','=',self.id)])

		
		promo_history_tree.unlink()

		if self.promotion.applicable_on == "product":
			sale_amount = 0
			sale_qty    = 0
			for x in invoice_lines:
				sale_amount = sale_amount + x.price_subtotal
				sale_qty = sale_qty + x.quantity
			refund_amount = 0
			refund_qty    = 0
			for x in invoice_lines_refund:
				refund_amount = refund_amount + x.price_subtotal
				refund_qty = refund_qty + x.quantity
			self.sale_value = sale_amount - refund_amount
			self.sale_quantity = sale_qty - refund_qty
			if self.promotion.scheme_type == "percentage_disc":
				if self.promotion.scheme == "value":
					for x in self.promotion.slabs:	
						if self.sale_value >= x.from_target and self.sale_value <= x.to_target:
								self.discount_percentage = x.discount_percentage
								self.target = x.target_name
								self.discounted_amount = (self.sale_value/100) * self.discount_percentage
				elif self.promotion.scheme == "qty":
					for x in self.promotion.slabs:	
						if self.sale_quantity >= x.from_target and self.sale_quantity <= x.to_target:
								self.discount_percentage = x.discount_percentage
								self.target = x.target_name
								self.discounted_amount = (self.sale_value/100) * self.discount_percentage
			
			elif self.promotion.scheme_type == "product_scheme":
				if self.promotion.scheme == "value":
					for x in self.promotion.prod_gift_base:	
						if self.sale_value >= x.from_target and self.sale_value <= x.to_target:
								self.product_gift = x.product_gift.id
								self.target = x.target_name
				elif self.promotion.scheme == "qty":
					for x in self.promotion.prod_gift_base:	
						if self.sale_quantity >= x.from_target and self.sale_quantity <= x.to_target:
								self.product_gift = x.product_gift.id
								self.target = x.target_name
			
			elif self.promotion.scheme_type == "points_scheme":
				# if self.promotion.prod_name.id == self.promotion.points_base.prod_name.id:
				# 	self.points_earned = (self.promotion.points_base.points/self.promotion.points_base.target_qty) * self.sale_quantity
				# else:
				# 	self.points_earned = 0
				if self.promotion.target_qty > 0:
					if self.promotion.scheme == "value":
						self.points_earned = ((self.sale_value/self.promotion.target_qty) * self.promotion.points)
					elif self.promotion.scheme == "qty":
						self.points_earned = ((self.sale_quantity/self.promotion.target_qty) * self.promotion.points)


			for x in invoice_lines:
				generate_history = promo_history_tree.create({
					 'date':x.invoice_id.date,
					 'product': x.product_id.id,
					 'category': x.product_id.categ_id.id,
					 'qty':x.quantity,
					 'unit_price':x.price_unit,
					 'total_price':x.price_subtotal,
					 'promo_customer_id':self.id,
					 })
			for x in invoice_lines_refund:
				generate_history = promo_history_tree.create({
					 'date':x.invoice_id.date,
					 'product': x.product_id.id,
					 'category': x.product_id.categ_id.id,
					 'qty':(x.quantity) * -1,
					 'unit_price':x.price_unit,
					 'total_price':(x.price_subtotal) * -1,
					 'promo_customer_id':self.id,
					 })

		elif self.promotion.applicable_on == "category":
			sale_amount = 0
			sale_qty    = 0
			for x in invoice_lines_cat:
				sale_amount = sale_amount + x.price_subtotal
				sale_qty = sale_qty + x.quantity
			refund_amount = 0
			refund_qty    = 0
			for x in invoice_lines_refund_cat:
				refund_amount = refund_amount + x.price_subtotal
				refund_qty = refund_qty + x.quantity
			self.sale_value = sale_amount - refund_amount
			self.sale_quantity = sale_qty - refund_qty
			if self.promotion.scheme_type == "percentage_disc":
					for x in self.promotion.slabs:	
						if self.sale_value > x.from_target and self.sale_value < x.to_target:
								self.discount_percentage = x.discount_percentage
								self.target = x.target_name
								self.discounted_amount = (self.sale_value/100) * self.discount_percentage
			
			elif self.promotion.scheme_type == "product_scheme":
					for x in self.promotion.prod_gift_base:	
						if self.sale_value > x.from_target and self.sale_value < x.to_target:
								self.product_gift = x.product_gift.id
								self.target = x.target_name

			elif self.promotion.scheme_type == "points_scheme":
				total_points = 0
				# for x in invoice_lines_cat:
				# 	for y in self.promotion.points_base:
				# 		print "xxxxxxxxxxxxxxxxxxxxxxxx"
				# 		if x.product_id.id == self.promotion.prod_name.id:
				# 		total_points = total_points + (y.points/y.target_qty) * x.quantity
				# for y in self.promotion.points_base:
				# 	# if self.sale_value <= y.target_qty:
				# 	total_points = total_points + ((self.sale_value/y.target_qty) * y.points)
				if self.promotion.target_qty > 0:
					total_points = ((self.sale_value/self.promotion.target_qty) * self.promotion.points)

				total_refund = 0
				for x in invoice_lines_refund_cat:
					for y in self.promotion.points_base:
						if x.product_id.id == self.promotion.prod_name.id:
							total_refund = total_refund + (y.points/y.target_qty) * x.quantity
				self.points_earned = total_points - total_refund

			for x in invoice_lines_cat:
				generate_history = promo_history_tree.create({
					 'date':x.invoice_id.date,
					 'product': x.product_id.id,
					 'category': x.product_id.categ_id.id,
					 'qty':x.quantity,
					 'unit_price':x.price_unit,
					 'total_price':x.price_subtotal,
					 'promo_customer_id':self.id,
					 })
			for x in invoice_lines_refund_cat:
				generate_history = promo_history_tree.create({
					 'date':x.invoice_id.date,
					 'product': x.product_id.id,
					 'category': x.product_id.categ_id.id,
					 'qty':(x.quantity) * -1,
					 'unit_price':x.price_unit,
					 'total_price':(x.price_subtotal) * -1,
					 'promo_customer_id':self.id,
					 })
		self.remaining_points = self.points_earned - self.points_consumed
#############################################
#Rewards on Points Customer 
#############################################
class sales_promo_rewards_customer(models.Model):
	_name 				= 'promo.rewards.customer'
	

	points 			= fields.Float(string = 'Points')
	product			= fields.Many2one('product.product',string ='Product')
	qty             = fields.Float(string = 'Qty')
	date 			= fields.Date(string="Date", required=True)
	# points_table 	= fields.Many2one('point_connection')	
	# discount 		= fields.Float(string = 'Discount')
	# product_gift    = fields.Many2one('product.product',string ='Gift')
	# availed 	    = fields.Selection([('product', 'Product'),
	# 										('discount','Discount'),
	# 										('gift','Gift Product'),
	# 										],string = "Availed")
	# units           = fields.Integer()
	
	promo_reward_id = fields.Many2one('points.consumption')
	validate_points_consume 	= fields.Boolean(string="Validate", default=False)

	# @api.onchange('product')
	# def on_change_points_consumption(self):
	# 	print self.product.list_price_own
	# 	# print "xxxxxxxxxxxxxxxxxxxxxxxx"
	# 	self.points=self.product.list_price_own

	@api.onchange('product','qty')
	def on_change_qty(self):
		if self.product and self.qty:
			self.points=self.product.standard_price * self.qty


	@api.onchange('validate_points_consume')
	def validatePoints(self):
		invoice = self.env['sale.order']
		invoice_lines = self.env['sale.order.line']
		if self.validate_points_consume == True:
			create_invoice = invoice.create({
				'partner_id': self.promo_reward_id.customer.id,
				# 'transporter':self.transporter.id,
				# 'remaining_payment_days':self.remaining_payment_days,
				# 'due' : self.due,
				# 'user_id' : self.user_id.id,
				# 'payment_term_id' : self.payment_term_id.id,
				# 'due_days' : self.due_days,
				'date_invoice' : self.date,
				# 'incoterm' : self.incoterm.id,
				'state' : "draft"
				})

			create_invoice_lines= invoice_lines.create({
				'product_id':self.product.id,
				'uom':"pcs",
				'product_uom':1,
				'product_uom_qty': 1,
				'quantity': self.qty,
				# 'carton': self.qty/self.product.pcs_per_carton,
				'last_sale': 0,
				# 'price': 0,
				'price_unit': 0,
				'discount': 0,
				'customer_price': 0,
				'price_subtotal': 0,
				# 'account_id': account_id,
				# 'name' : x.name,
				'invoice_id' : create_invoice.id,
				'order_id':create_invoice.id,
				})


		# purchase = self.env['purchase.order']
		# purchase_lines = self.env['purchase.order.line']
		# create_purchase = purchase.create({
		# 	'partner_id': self.promo_reward_id.customer.id,
		# 	# 'date_order':
		# 	# 'transporter':self.transporter.id,
		# 	# 'remaining_payment_days':self.remaining_payment_days,
		# 	# 'due' : self.due,
		# 	# 'user_id' : self.user_id.id,
		# 	# 'payment_term_id' : self.payment_term_id.id,
		# 	# 'due_days' : self.due_days,
		# 	'date_invoice':self.date,
		# 	# 'incoterm' : self.incoterm.id,
		# 	'state' : "draft"
		# 	})

		# create_purchase_lines= purchase_lines.create({
		# 	'product_id':2,
		# 	'name':"Testing this product",
		# 	'date_planned':"06/22/2017",
		# 	'product_qty': 1,
		# 	'product_uom':1,
		# 	# 'quantity': self.qty,
		# 	# 'carton': self.qty/self.product.pcs_per_carton,
		# 	# 'last_sale': 0,
		# 	# 'price': 0,
		# 	'price_unit': 0,
		# 	# 'discount': 0,
		# 	# 'customer_price': 0,
		# 	'price_subtotal': 0,
		# 	# 'account_id': account_id,
		# 	# 'name' : x.name,
		# 	# 'invoice_id' : create_invoice.id,
		# 	'order_id':create_purchase.id,
		# 	})
	# @api.multi
	# def ValidatePoints(self):
	# 	print "xxxxxxxxx"
	# 	print "Create Sale Order"
	# 	invoice = self.env['sale.order']
	# 	invoice_lines = self.env['sale.order.line']
	# 	create_invoice = invoice.create({
	# 		'partner_id': self.promo_reward_id.customer.id,
	# 		# 'transporter':self.transporter.id,
	# 		# 'remaining_payment_days':self.remaining_payment_days,
	# 		# 'due' : self.due,
	# 		# 'user_id' : self.user_id.id,
	# 		# 'payment_term_id' : self.payment_term_id.id,
	# 		# 'due_days' : self.due_days,
	# 		'date_invoice' : self.date,
	# 		# 'incoterm' : self.incoterm.id,
	# 		'state' : "draft"
	# 		})

	# 	create_invoice_lines= invoice_lines.create({
	# 		'product_id':self.product.id,
	# 		'uom':self.product.uom,
	# 		'quantity': self.qty,
	# 		'carton': self.qty/self.product.pcs_per_carton,
	# 		'last_sale': 0,
	# 		# 'price': 0,
	# 		'price_unit': 0,
	# 		'discount': 0,
	# 		'customer_price': 0,
	# 		'price_subtotal': 0,
	# 		# 'account_id': account_id,
	# 		# 'name' : x.name,
	# 		'invoice_id' : create_invoice.id
	# 		})


class account_invoice_line_history(models.Model):
	_name 				= 'promo.history'
	
	date                 = fields.Date()
	category             = fields.Many2one('product.category')
	total_price          = fields.Float(string = "Total Price")
	qty                  = fields.Float(string = "Quantity")
	unit_price           = fields.Float(string = "Unit Price")
	product              = fields.Many2one('product.product',string = "Product")

	promo_customer_id    = fields.Many2one('promo.customer')


# class sale_order_extension(models.Model):
# 	_inherit = 'sale.order'

# ###################################################
# 	due_days =fields.Float()
# 	incoterm = fields.Char()
# 	due = fields.Char()
# 	transporter = fields.Char()
# ###################################################
# 	instant_promo = fields.One2many('instant.promo.so','instant_promo_id')

# 	@api.model
# 	def create(self, vals):
# 		new_record = super(sale_order_extension, self).create(vals)
# 		self.delete_zero_products()
# 		return new_record

# 	@api.multi
# 	def write(self, vals):
# 		super(sale_order_extension, self).write(vals)
# 		self.delete_zero_products()
# 		return True
# 	def delete_zero_products(self):
# 		for lines in self.instant_promo:
# 			if lines.qty == 0:
# 				lines.unlink()


# 	@api.multi
# 	def action_confirm(self):
# 		for lines in self.instant_promo:
# 			self.order_line.create({
# 				'product_id': lines.product_id.id,
# 				'product_uom_qty':lines.qty,
# 				'price_unit': 0,
# 				'order_id':self.id
# 				})
# 		return super(sale_order_extension,self).action_confirm()





# 	@api.onchange('order_line')
# 	def on_change_instant_promo(self):
# 		instant_promo_lines = self.env['promo.instant'].search([('sales_promo_id5.scheme_from_dt','<',self.date_order), ('sales_promo_id5.scheme_to_dt','>',self.date_order), ('sales_promo_id5.stages','=',"validate")])
# 		sale_order_lines = self.env['sale.order.line'].search([])

# 		for x in self.order_line:
# 			for y in instant_promo_lines:
# 				if x.product_id.id == y.product.id and x.order_id.partner_id in y.sales_promo_id5.customer:
# 					invoice_lines = self.env['account.invoice.line'].search([('invoice_id.date','>',y.sales_promo_id5.scheme_from_dt), ('invoice_id.date','<',y.sales_promo_id5.scheme_to_dt),('product_id.id','=',y.product.id),('invoice_id.partner_id.id','=',self.partner_id.id),('invoice_id.state','!=',"draft")])
					
# 					current_quantity = 0
# 					for qt in self.order_line:
# 						if qt.product_id.id == y.product.id and qt.price_unit != 0:
# 							current_quantity = current_quantity + qt.product_uom_qty
# 					invoice_total = (self.quantity(invoice_lines)[0] - self.quantity(invoice_lines)[2]) + current_quantity
# 					invoice_total_promo =  self.quantity(invoice_lines)[1] - self.quantity(invoice_lines)[3]
# 					reward_quantity = (int(invoice_total/y.qty) * y.qty_reward) - invoice_total_promo  
					
# 					ids = []
# 					for a in self.instant_promo:
# 						ids.append(a.product_id.id)
# 					if x.product_id.id not in ids and reward_quantity > 0:
# 						self.instant_promo |= self.instant_promo.new({'product_id':x.product_id.id,'qty': reward_quantity,'instant_promo_id': self.id,})
# 					elif x.product_id.id in ids:
# 						for c in self.instant_promo:
# 							if c.product_id.id == x.product_id.id:
# 								c.qty = reward_quantity

# 		product_lst = []
# 		for y in self.order_line:
# 			product_lst.append(y.product_id.id)
# 		for lines in self.instant_promo:
# 			if lines.product_id.id not in product_lst:
# 				lines.qty = 0


				
	
# 	def quantity(self,invoice):
# 		total_quantity = [0,0,0,0]
# 		for z in invoice:
# 			if z.invoice_id.type == "out_invoice":
# 				if z.price_unit != 0:
# 					total_quantity[0] = total_quantity[0] + z.quantity
# 				else:
# 					total_quantity[1] = total_quantity[1] + z.quantity
# 			elif z.invoice_id.type == "out_refund":
# 				if z.price_unit != 0:
# 					total_quantity[2] = total_quantity[2] + z.quantity
# 				else:
# 					total_quantity[3] = total_quantity[3] + z.quantity
# 		return total_quantity

class instant_promo_so(models.Model):
	_name = 'instant.promo.so'

	product_id = fields.Many2one('product.product', string = "Product")
	qty        = fields.Float(string = "Quantity")

	instant_promo_id = fields.Many2one('sale.order')


class generate_products(models.TransientModel):
	_name = "generate.products"

	category = fields.Many2one('product.category')


	
	@api.multi
	def generate(self):
		active_class =self.env['naseem.sales.promo'].browse(self._context.get('active_id'))
		all_products = self.env['product.product'].search([])
		products_tree_view = self.env['promo.instant'].search([('sales_promo_id5','=',active_class.id)])
		products_tree_view.unlink()        
		for x in all_products:
			if x.categ_id.id == self.category.id:
				generate_products_tree = products_tree_view.create({
					'product': x.id,
					'sales_promo_id5':active_class.id,
					})
		

class AccountMoveRemoveValidation(models.Model):
	_inherit = "account.move"

	promo_id 	= fields.Integer(string="Pomotion ID")
	tt_serial 	= fields.Char(string="TT Serial")

	@api.multi
	def assert_balanced(self):
		if not self.ids:
			return True
		prec = self.env['decimal.precision'].precision_get('Account')

		self._cr.execute("""\
			SELECT      move_id
			FROM        account_move_line
			WHERE       move_id in %s
			GROUP BY    move_id
			HAVING      abs(sum(debit) - sum(credit)) > %s
			""", (tuple(self.ids), 10 ** (-max(5, prec))))
		# if len(self._cr.fetchall()) != 0:
		#     raise UserError(_("Cannot create unbalanced journal entry."))
		return True


class PointsConsumption(models.Model):
	_name="points.consumption"

	customer 		= fields.Many2one("res.partner", required=True)
	total_points 	= fields.Float(string="Total Points")
	point_cons 		= fields.Float(string="Points Consumed")
	rem_point 		= fields.Float(string="Remaining Points")
	promo_rewards 	= fields.One2many('promo.rewards.customer','promo_reward_id')
	state 			= fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirm'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
	# point_connection 	= fields.Many2one('promo.rewards.customer')

	@api.onchange('promo_rewards')
	def _on_change(self):
		total_p = 0
		for x in self.promo_rewards:
			total_p = total_p + x.points
		self.point_cons = total_p

	@api.onchange('total_points','point_cons')
	def _remaining_points(self):
		self.rem_point = self.total_points - self.point_cons

	def UpdatePoints(self):
		all_customer = self.env['promo.customer'].search([])
		total_p=0
		for x in all_customer:
			if x.customer.id == self.customer.id:
				total_p = total_p + x.points_earned
		self.total_points = total_p
		return
	@api.multi
	def confirmPoints(self):
		self.state = "confirm"

	# @api.onchange('customer')
	# def UpdatePoints(self):
	# 	all_customer = self.env['promo.customer'].search([])
	# 	total_p=0
	# 	for x in all_customer:
	# 		if x.customer.id == self.customer.id:
	# 			total_p = total_p + x.points_earned
	# 	self.total_points = total_p
	# 	return



	# @api.multi
	# def ValidatePoints(self):

	# 	print "xxxxxxxxxxxxxxxxx"
	# 	print "xxxxxxxxxxxxxxxxx"
	# 	print "xxxxxxxxxxxxxxxxx"
		# invoice = self.env['account.invoice'].search([])
		# invoice_lines = self.env['account.invoice.line'].search([])
		# create_invoice = invoice.create({
		# 	'journal_id': self.journal.id,
		# 	'partner_id':self.partner_id.id,
		# 	'transporter':self.transporter.id,
		# 	'remaining_payment_days':self.remaining_payment_days,
		# 	'due' : self.due,
		# 	'user_id' : self.user_id.id,
		# 	'payment_term_id' : self.payment_term_id.id,
		# 	'due_days' : self.due_days,
		# 	'date_invoice' : self.date_order,
		# 	'incoterm' : self.incoterm.id,
		# 	'state2' : "confirm"
		# 	})

		# for x in self.order_line:
		# 	if x.product_id.property_account_income_id.id:
		# 		account_id = x.product_id.property_account_income_id.id
		# 	else:
		# 		account_id = x.product_id.categ_id.property_account_income_categ_id	
		# 	create_invoice_lines= invoice_lines.create({
		# 		'product_id':x.product_id.id,
		# 		'uom':x.uom,
		# 		'quantity': x.product_uom_qty,
		# 		'carton': x.carton,
		# 		'last_sale': x.last_sale,
		# 		'price': x.price.id,
		# 		'price_unit': x.price_unit,
		# 		'discount': x.discount,
		# 		'customer_price': x.customer_price,
		# 		'price_subtotal': x.price_subtotal,
		# 		'promo_code': x.promo_code,
		# 		'account_id': account_id,
		# 		'name' : x.name,
		# 		'invoice_id' : create_invoice.id
		# 		})	
		# journal_entries = self.env['account.move'].search([])
		# journal_entries_lines = self.env['account.move.line'].search([])

		# if self.promo_rewards.product.name == 'discount':
		# 	create_journal_entry = journal_entries.create({
		# 			'journal_id': 1,
		# 			'date':self.date,
		# 			'promo_id':self.id,
		# 			})
		# 	create_line = journal_entries_lines.create({
		# 		'account_id':1,
		# 		'partner_id':self.customer.id,
		# 		'name':"test",
		# 		'debit':self.promo_rewards.points,
		# 		'move_id':create_journal_entry.id
		# 		})

class directInvoice(models.Model):
	_inherit='account.invoice'

	# customer_price = fields.Float()

	picking_type= fields.Many2one('stock.picking.type')
	location_id = fields.Many2one('stock.location')
	location_dest = fields.Many2one('stock.location')
########################################

########################################
	

	@api.multi
	def createDelivery(self):
		inventory = self.env['stock.picking'].search([])
		inventory_lines = self.env['stock.move'].search([])
		create_inventory = inventory.create({
			'partner_id':self.partner_id.id,
			'picking_type_id': self.picking_type.id,
			'location_id':self.location_id.id,
			'location_dest_id': self.location_dest.id,
			})
		for x in self.invoice_line_ids:
			create_inventory_lines= inventory_lines.create({
				'product_id':x.product_id.id,
				'product_uom_qty':x.quantity,
				'product_uom': x.product_id.uom_id.id,
				'location_id':self.location_id.id,
				'picking_id': create_inventory.id,
				'name':"test",
				'location_dest_id': self.location_dest.id,
				})










