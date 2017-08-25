# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp import _
from openerp.exceptions import Warning
from odoo.exceptions import UserError


class pricelist_product_configuration(models.Model):
	_name = 'pricelist.configuration'
	_rec_name = 'category'


	@api.multi
	def unlink(self):
		raise UserError('You cannot Delete any pricelist')
		# return True

	@api.onchange('customer','category')
	def generate_check_list(self):
		if self.category:
			self.check_list = str(self.category.name) + " " + str(self.customer.name)

	@api.onchange('type_pricelist')
	def check_list_type(self):
		if self.type_pricelist == "normal":
			self.customer = False

	@api.one
	@api.constrains('category','type_pricelist','customer','stages')
	def _check_date(self):

		all_cat_ids = self.env['pricelist.configuration'].search([('id','!=',self.id),('stages','!=',"inactivate")])
		for x in all_cat_ids:
			if self.check_list == x.check_list:
				raise ValidationError('Category already exists')

		# all_ids = []
		# all_customers = []
		# for x in all_cat_ids:
		# 	if x.id != self.id and x.stages != "inactivate":
		# 		all_ids.append(x.category.id)
		# 		all_customers.append(x.customer.id)
		# if self.type_pricelist == "normal":
		# 	if x.category.id in all_ids:
		# 		raise ValidationError('Category already exists')
		# elif self.type_pricelist == "customer":
		# 	if x.category.id in all_ids and x.customer.id in all_customers:
		# 		raise ValidationError('Category for this customer already exists')


	category 			= fields.Many2one('product.category' , required = True)
	category_discount 	= fields.Float('Discount')
	get_products_id 	= fields.One2many('get.products','pricelist_configuration')
	get_products_id1 	= fields.One2many('get.products','pricelist_configuration')
	get_products_id2 	= fields.One2many('get.products','pricelist_configuration')
	customer 			= fields.Many2one('res.partner',domain="[('customer','!=', False)]")
	check_list 			= fields.Char(string="Check Lists")
	type_pricelist     	= fields.Selection([
		('normal', 'Normal'),
		('customer', 'Customer Based'),
		],default='normal')
	based_on     = fields.Selection([
		('discount_cat', 'Discount Category Wise'),
		('discount_prod', 'Discount Product Wise'),
		('fixed_price', 'Fixed Price'),
		],string = "Based On")
	stages     = fields.Selection([
		('draft', 'Draft'),
		('validate', 'Validate'),
		('inactivate', 'Deactivate'),
		],string = "Stages", default = 'draft')
	unique_record_name = fields.Char()





	@api.multi
	def generate_products(self):
		all_products = self.env['product.product'].search([])
		products_tree_view = self.env['get.products'].search([])
		emp_list = []
		for x in self.get_products_id:
			emp_list.append(x.product_id.id)
		all_prod = []
		for x in all_products:
			if x.categ_id.id == self.category.id:
				all_prod.append(x.id)
			if x.categ_id.id == self.category.id and x.id not in emp_list:
				generate_products_tree = products_tree_view.create({
					'product_id': x.id,
					'pricelist_configuration':self.id,
					})

		for y in emp_list:
			if y not in all_prod:
				product = self.env['get.products'].search([('product_id.id','=',y)])
				for z in product:
					z.unlink()


	@api.multi
	def validate(self):
		self.stages = "validate"


	# @api.multi
	# def activation(self):
	# 	if self.category:
	# 		pricelists = self.env['pricelist.configuration'].search([('category','=',self.category.id),('stages','!=',"inactivate")])
	# 	if not pricelists:
	# 		self.stages = 'validate'
	# 	else:
	# 		raise Warning(_('Another pricelist of this Category already exists in active state'))



	@api.multi
	def inactive_pricelist(self):

		if self.type_pricelist=="normal":
			for x in self.get_products_id:
				pricelist = self.env['product.pricelist.item'].search([('config_id','=', x.id)])
				for y in pricelist:
					y.unlink()
			for x in self.get_products_id:
				product = self.env['product.product'].search([('name','=', x.product_id.name)])
				product.list_price_own = 0
				product.level_1 = 0
				product.level_2 = 0
				product.level_3 = 0



		# pricelist1 = self.env['product.pricelist'].search([('name','=', "Level 1")])
		# pricelist2 = self.env['product.pricelist'].search([('name','=', "Level 2")])
		# pricelist3 = self.env['product.pricelist'].search([('name','=', "Level 3")])
		# pricelist = self.env['product.pricelist'].search([('name','=', "List Price")])
		# for x in pricelist.item_ids:
		# 	for y in self.get_product_id:
		# 		if x.product_id.id == y.product_id.id and x.product_id.categ_id == y.product_id.categ_id:
		# 			x.unlink()
		# for x in pricelist1.item_ids:
		# 	for y in self.get_product_id:
		# 		if x.product_id.id == y.product_id.id and x.product_id.categ_id == y.product_id.categ_id:
		# 			x.unlink()
		# for x in pricelist2.item_ids:
		# 	for y in self.get_product_id:
		# 		if x.product_id.id == y.product_id.id and x.product_id.categ_id == y.product_id.categ_id:
		# 			x.unlink()
		# for x in pricelist3.item_ids:
		# 	x.unlink()


		if self.based_on == "discount_cat":
			for x in self.customer.linked_pricelist.item_ids:
				if x.config_id == str(self.id)+" " + str(self.based_on):
					x.unlink()


		if self.based_on == "fixed_price":
			for y in self.get_products_id2:
				for x in self.customer.linked_pricelist.item_ids:
					if x.config_id == str(y.id)+" " + str(self.based_on):
						x.unlink()


		if self.based_on == "discount_prod":
			for y in self.get_products_id1:
				for x in self.customer.linked_pricelist.item_ids:
					if x.config_id == str(y.id)+" " + str(self.based_on):
						x.unlink()

		self.stages="inactivate"


	@api.multi
	def update_pricelist_rule(self,product,price,pricelist_name,line_id,applied,price_compute,base,base_pricelist_id,price_discount,categ_id):
		
		pricelist = self.env['product.pricelist'].search([('name','=', pricelist_name)])
		pricelists_rules = self.env['product.pricelist.item'].search([('config_id','=',line_id),('pricelist_id','=',pricelist.id)])
		if not pricelists_rules:
			create_new_rule_list = pricelists_rules.create({
						'applied_on':applied,
						'compute_price':price_compute,
						'product_id':product,
						'fixed_price':price,
						'pricelist_id':pricelist.id,
						'config_id':line_id,
						'base':base,
						'base_pricelist_id':base_pricelist_id,
						'price_discount': price_discount,
						'categ_id':categ_id,
						'name':str(pricelists_rules.pricelist_id.name) + " - " + str(pricelists_rules.fixed_price)
						})
		else:
			if self.based_on == "fixed_price" or self.type_pricelist == "normal":
				pricelists_rules.fixed_price = price
				pricelists_rules.name = str(pricelists_rules.pricelist_id.name) + " - " + str(pricelists_rules.fixed_price)
			else:
				pricelists_rules.price_discount = price_discount

	@api.multi
	def update_pricelist(self):

		self.stages="validate"


		pricelists_list_price = self.env['product.pricelist'].search([('name','=', "List Price")])
		if self.type_pricelist == "normal":
			for items in self.get_products_id:
				self.update_pricelist_rule(items.product_id.id,items.list_price,"List Price",items.id,"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)
				self.update_pricelist_rule(items.product_id.id,items.price_level1,"Level 1",items.id,"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)
				self.update_pricelist_rule(items.product_id.id,items.price_level2,"Level 2",items.id,"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)
				self.update_pricelist_rule(items.product_id.id,items.price_level3,"Level 3",items.id,"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)

				items.product_id.list_price_own = items.list_price
				items.product_id.level_1 = items.price_level1
				items.product_id.level_2 = items.price_level2
				items.product_id.level_3 = items.price_level3
		else:
			if not self.customer.linked_pricelist:
				create_new_pricelist = pricelists_list_price.create({
					'name': self.customer.name,
					})
				self.customer.linked_pricelist = create_new_pricelist.id

			if self.based_on == "fixed_price":
				for y in self.get_products_id2:
					self.update_pricelist_rule(y.product_id.id,y.fixed_price,self.customer.name,str(y.id)+" " + str(self.based_on),"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)
					# self.update_pricelist_rule(y.product_id.id,y.fixed_price,create_new_pricelist.name,str(y.id)+" " + str(self.based_on),"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)

			elif self.based_on == "discount_cat":
				self.update_pricelist_rule(None,None,self.customer.name,str(self.id)+" " + str(self.based_on),"2_product_category","formula","pricelist",2,self.category_discount,self.category.id)
			elif self.based_on == "discount_prod":
			     for prod in self.get_products_id1:
					self.update_pricelist_rule(prod.product_id.id,None,self.customer.name,str(prod.id)+" "+str(self.based_on),"0_product_variant","formula","pricelist",2,prod.discount_percentage,None)





class PricelistLineExtension(models.Model):
	_inherit = 'product.pricelist.item'



	name = fields.Char(compute=None)
	config_id = fields.Char()
	categ_id = fields.Many2one(
        'product.category', 'Product Category',required = False, ondelete='cascade',
        help="Specify a product category if this rule only applies to products belonging to this category or its children categories. Keep empty otherwise.")
	base = fields.Selection([
		('list_price', 'Public Price'),
		('standard_price', 'Cost'),
		('pricelist', 'Other Pricelist')], "Based on",
		default='list_price',required = False,
		help='Base price for computation.\n'
		'Public Price: The base price will be the Sale/public Price.\n'
		'Cost Price : The base price will be the cost price.\n'
		'Other Pricelist : Computation of the base price based on another Pricelist.')




	@api.model
	def create(self, vals):
		new_record = super(PricelistLineExtension, self).create(vals)
		new_record.name = str(new_record.pricelist_id.name) + " - " + str(new_record.fixed_price)

		return new_record





class link_pricelist(models.Model):
	_inherit = 'res.partner'

	linked_pricelist = fields.Many2one('product.pricelist', string = "Linked Pricelist", readonly = True)
	


# class sale_order_line(models.Model):
# 	_inherit = 'sale.order.line'

# 	pricelist_ext = fields.Many2one('product.pricelist', string = "Pricelist")
# 	price = fields.Many2one('product.pricelist.item')
# 	check_boolean = fields.Boolean()
# 	set_list_price = fields.Boolean()
	



# 	@api.onchange('product_id')
# 	def check_pricelist(self):
# 		if self.product_id:
# 			pricelist = self.env['product.pricelist'].search([('id','=',self.order_id.partner_id.linked_pricelist.id)])
# 			pricelist_lines = self.env['product.pricelist.item'].search([('pricelist_id','=',pricelist.id)])
# 			for x in pricelist_lines:
# 				if x.product_id.id == self.product_id.id or x.categ_id.id == self.product_id.categ_id.id:
# 					self.pricelist_ext = self.order_id.partner_id.linked_pricelist.id
# 					self.check_boolean = True
			

# 	@api.onchange('price')
# 	def get_price(self):
# 	   self.pricelist_ext = self.price.pricelist_id.id

# 	@api.multi
# 	def _get_display_price(self, product):
# 	   if self.order_id.pricelist_id.discount_policy == 'without_discount':
# 		  from_currency = self.order_id.company_id.currency_id
# 		  return from_currency.compute(product.lst_price, self.pricelist_ext.currency_id)
# 	   return product.with_context(pricelist=self.pricelist_ext.id).price

# 	@api.multi
# 	@api.onchange('product_id','pricelist_ext')
# 	def product_id_change(self):
# 		if not self.product_id:
# 			return {'domain': {'product_uom': []}}

# 		vals = {}
# 		domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
# 		if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
# 			vals['product_uom'] = self.product_id.uom_id
# 			vals['product_uom_qty'] = 1.0

# 		product = self.product_id.with_context(
# 			lang=self.order_id.partner_id.lang,
# 			partner=self.order_id.partner_id.id,
# 			quantity=vals.get('product_uom_qty') or self.product_uom_qty,
# 			date=self.order_id.date_order,
# 			pricelist=self.pricelist_ext.id,
# 			uom=self.product_uom.id
# 			)
# 		name = product.name_get()[0][1]
# 		if product.description_sale:
# 			name += '\n' + product.description_sale
# 		vals['name'] = name

# 		self._compute_tax_id()

# 		if self.pricelist_ext and self.order_id.partner_id:
# 			vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
# 		self.update(vals)

# 		title = False
# 		message = False
# 		warning = {}
# 		if product.sale_line_warn != 'no-message':
# 			title = _("Warning for %s") % product.name
# 			message = product.sale_line_warn_msg
# 			warning['title'] = title
# 			warning['message'] = message
# 			if product.sale_line_warn == 'block':
# 				self.product_id = False
# 			return {'warning': warning}
# 		return {'domain': domain}
		


class get_products_category(models.Model):
	_name = 'get.products'

	product_id               = fields.Many2one('product.product',string = "Product", readonly = "True" , required = True)
	list_price               = fields.Float   (string = "List Price")
	price_level1             = fields.Float (string = "Level 1")
	price_level2             = fields.Float (string = "Level 2")
	price_level3             = fields.Float (string = "Level 3")
	fixed_price              = fields.Float (string = "Fixed Price")
	discount_percentage      = fields.Float (string = "Discount Percentage")
	category                 = fields.Many2one ('product.category')
	pricelist_configuration  = fields.Many2one('pricelist.configuration')

	@api.multi
	def unlink(self):
		super(get_products_category,self).unlink()
		pricelist = self.env['product.pricelist.item'].search([('config_id','=', self.id)])
		for x in pricelist:
			x.unlink()

		return True
