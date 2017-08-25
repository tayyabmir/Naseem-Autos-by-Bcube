# -*- coding: utf-8 -*- 
from odoo import models, fields, api
import datetime
from datetime import datetime,date,timedelta,time
from openerp.osv import osv
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from odoo.exceptions import UserError
class product_order_extension(models.Model): 
	_inherit = 'purchase.order'


	
	is_complete 		= fields.Boolean()
	scheduled_date 		= fields.Date(string="Scheduled Date",default=datetime.today())
	departure_date 		= fields.Date(string="Departure Date",default=datetime.today())
	contact			 	= fields.Char(string="Contact No.")
	adress 				= fields.Char(string="Adress")
	incoterm 			= fields.Many2one('stock.incoterms', string="Delivery Term")
	payment_term_method = fields.Many2one('account.payment.term', string="Payment Term")
	# payment_term_id 	= fields.Many2one('account.payment.term', string="Payment Term")
	ETA 				= fields.Date(string="ETA")
	ETD 				= fields.Date(string="ETD")
	n_weight			= fields.Float(string="Net Weight")
	g_weight			= fields.Float(string="Gross Weight")
	CBM 				= fields.Float(string="CBM")
	# lc_costing_link 	= fields.One2many('lc.costing','lc_costing_tab')
	lc_costing_link 	= fields.One2many('lc.costing','lc_costing_link_po')

	shipping_doc_link 	= fields.One2many('shipping.document.attachment','shipping_doc_tree')
	# purchase_product_wizard = fields.Boolean(string="")

	transporter 		= fields.Many2one('res.partner', string="Transporter")
	forwarder 			= fields.Many2one('res.partner', string="Forwarder")
	clearing_agent 		= fields.Many2one('res.partner', string="Clearing Agent")

	ship_line 			= fields.Many2one('shipping.line')



##################### Shipping Details ########################### 
	invoice_address = fields.Char(string="Invoice Address")
	port 			= fields.Many2one('destination.port',string="POD")
	loading_port 	= fields.Many2one('loading.port',string="POL")
	bl_no 			= fields.Char(string="B/L No.")
	vessel 			= fields.Char(string="Vessel")
	container 		= fields.Char(string="Container #")
	ship_mark 		= fields.Char(string="Ship. Mark")
	performa 		= fields.Char(string="Supplier Invoice No.")
	sro 			= fields.Char(string="SRO #")
	s_tax_serial 	= fields.Char(string="GD No.")
	cnic 			= fields.Char(string="CNIC no")
	ntn 			= fields.Char(string="NTN Number")
	style 			= fields.Char(string="Style")
	Color 			= fields.Char(string="Color")
	qty_ctn 		= fields.Char(string="Qty/CTN")
	lot 			= fields.Char(string="Lot")
	pin 			= fields.Char(string="Pin")
	partial_shipment = fields.Char(string="Partial Shipment")
	transhipment 	= fields.Char(string="transhipment")
	e_form_no 		= fields.Char(string="E Form No")

	# ship_to_address = fields.Text(string="Ship To Address")
	# bill_to_address = fields.Text(string="Bill To Address")
	# notify = fields.Text(string="Notify")
	# other_notify = fields.Text(string="Other Notify")

	gross_weight = fields.Float(string="Gross Weight")
	net_weight = fields.Float(string="Net Weight")
	incoterm_price = fields.Float(string="Inco Term Price")

	etd_khi = fields.Date(string="ETD")
	eta_ship = fields.Date(string="ETA")    
	cbm_ship = fields.Float(string="CBM")
	bl_date = fields.Date(string="B/L Date")
	form_e_date = fields.Date(string="E Form Date")
	delivery_date = fields.Date(string="Delivery Date")
	confirmation_date = fields.Date(string="Confirmation Date")

	invoice_bank = fields.Many2one('res.bank',string="Bank")
	bank_account = fields.Many2one('account.journal',string="Bank")
	employee_name = fields.Many2one('hr.employee',string="Employee Name")
	# inco_terms = fields.Many2one('stock.incoterms',string="Inco Terms")

	state = fields.Selection([
		('draft', 'RFQ'),
		('sent', 'RFQ Sent'),
		('to approve', 'To Approve'),
		('purchase', 'Purchase Order'),
		('done', 'Locked'),
		('cancel', 'Cancelled'),
		('partial', 'Partial'),
		('complete', 'Complete'),
		],string="Custom Stages", default="draft")

	ship_via = fields.Selection([
		('bysea', 'By Sea'),
		('byair', 'By Air'),
		('byland', 'By Land'),
		],default='bysea', string="Ship via")
	ship_mode = fields.Selection([
		('bysea', 'By Sea'),
		('byair', 'By Air'),
		('byland', 'By Land'),
		],default='bysea', string="Ship Mode")

  
#--------------------------------More Detailes Variables----------------------------------------------

	company 			= fields.Char("Company")
	payments_terms 		=fields.Char("Payments Terms")
	shipment 			= fields.Char("Shipment of")
	remarks 			= fields.Char("Remarks")
	narration_1 		= fields.Text("Narration for LC (I)")
	narration_2 		= fields.Text("Narration for LC (II)")
	through_1 			= fields.Text("Through")
	applicant 			= fields.Text("Applicant")
	rebate_percentage 	= fields.Text("Rebate Percentage")
	more_info 			= fields.Text("More Info")
	under_claim 		= fields.Char("Under Claim For Rebate")
	airline 			= fields.Char("Airline")
	through_2			= fields.Char("Through")
	des 				= fields.Char("Description")
	carton_size 		= fields.Char("Carton Size")
	frieght 			=fields.Char("Frieght")
	hawb_no 			= fields.Char("H.A.W.B No")
	LC_no 				= fields.Char("LC No")
	Lc_amt 				= fields.Float("LC Amt")
	Lc_date 			= fields.Date("LC Date")
	HS_code 			= fields.Char("HS Code")
	manual_serial_no 	= fields.Char("Manual Serial #")
	manual_date 		= fields.Date("Manual Date")
	container_size 		= fields.Char("Container Size")

	amount_total_footer = fields.Float(string="Total",readonly=True)
	per_dollar_cost 	= fields.Float(string="Per Dollar Cost")
	tt_total_amount 	= fields.Float(string="TT Total Amount")


	other_expense_link 	= fields.One2many('other.expense','other_expense_tree')

#-----------------------------------------

# CBM Container Size

	awb_no=fields.Char("AWB No.")
	awb_date=fields.Date("AWB Date")

	def button_cancel(self):
		product_details = self.env['product.product'].search([('default_code','=',self.product_id.default_code),('name','=',self.product_id.name)])
		for x in product_details.history_link:
			if x.po_no == self.name:
				x.unlink()
		super(product_order_extension, self).button_cancel()

	@api.multi
	def average_price_product(self):
		for x in self.order_line:
			product_details = self.env['product.product'].search([('default_code','=',x.product_id.default_code),('name','=',x.product_id.name)])
			forecast_value = self.env['report.stock.forecast'].search([('product_id','=',x.product_id.id)])
			history = self.env['product.history'].search([])
			if x.avg_status == False:	
				pre_quantity = forecast_value.quantity - x.product_qty
				new_net = pre_quantity
				old_avg_price = new_net * product_details.average_cost
				new_avg_price = x.product_qty * x.price_unit 
				calculate_average = (old_avg_price + new_avg_price) / (x.product_qty + new_net)

				create_history_line = history.create({
								'date':self.date_order,
								'qty':x.qty_received,
								'unit_price':x.price_unit,
								'pre_qty':pre_quantity,
								'adjustment':0,
								'net':pre_quantity,
								'pre_price':product_details.average_cost,
								'avg_price':calculate_average,
								'po_qty':x.product_qty,
								'po_no':self.name,
								'history_id':product_details.id,
								})

				product_details.previouse_purchase 	= product_details.previouse_purchase + x.price_unit
				product_details.previouse_qty		= product_details.previouse_qty + x.product_qty
				product_details.average_cost		= calculate_average
				x.avg_status = True
			
		for y in product_details.history_link:
			new_net = y.net - y.adjustment
			old_avg_price = new_net * product_details.average_cost
			new_avg_price = y.po_qty * y.unit_price 
			calculate_average = (old_avg_price + new_avg_price) / (y.po_qty + new_net)
			self.avg_price = calculate_average



	@api.onchange('ETA','ETD','CBM','n_weight','g_weight','partner_ref')
	def get_shipping_est(self):
		if self.ETA:
			self.eta_ship = self.ETA
		if self.ETD:
			self.etd_khi = self.ETD
		if self.partner_ref:
			self.performa = self.partner_ref
		if self.CBM:
			self.cbm_ship = self.CBM
		if self.n_weight:
			self.net_weight = self.n_weight
		if self.g_weight:
			self.gross_weight = self.g_weight

	@api.multi
	def complete_order(self):
		if self.tt_total_amount == self.amount_total:
			self.state = "complete"
			back_order = self.env['stock.picking'].search([('origin','=',self.name),('state','not in',('done','cancel'))])
			if back_order:
				back_order.state = "cancel"
		else:
			raise UserError('Total PO Amount and Punched TT Amount is not Equal')



	@api.multi
	def submitt_expense(self):
		for x in self.other_expense_link:
			journal_entries = self.env['account.move'].search([('promo_id','=',x.id)])
			vendor_bill = self.env['account.invoice'].search([('type','=',"in_invoice"),('id','=',x.id)])
			invoice_lines = self.env['account.invoice.line'].search([])
			journal_entries_lines = self.env['account.move.line'].search([])
			if x.status == False:
				if not journal_entries:
					if x.bank_type:
						create_journal_entry = journal_entries.create({
							'journal_id': x.bank_type.id,
							'date':x.expense_date,
							'promo_id':x.id,
							'ref':x.description,
							})
						create_debit = journal_entries_lines.create({
							'account_id':1,
							'partner_id':self.partner_id.id,
							'name':self.partner_id.name,
							'debit':x.amount,
							'move_id':create_journal_entry.id
							})
						create_credit = journal_entries_lines.create({
							'account_id':3,
							'partner_id':self.partner_id.id,
							'name':self.partner_id.name,
							'credit':x.amount,
							'move_id':create_journal_entry.id
							})
				elif not vendor_bill:	
					if not x.bank_type:
						create_invoice = vendor_bill.create({
							'partner_id':x.vendor_name.id,
							'reference':x.expense_type.name,
							'date_invoice':x.expense_date,
							'date_due':x.expense_date,
							'type':"in_invoice",
							})

						create_invoice_lines= invoice_lines.create({
							'name' : x.expense_type.name,
							'account_id' : x.expense_type.haulage_journal.id,
							'price_unit' : x.amount,
							'price_subtotal' : x.amount,
							'invoice_id' : create_invoice.id
							})
				x.status = True
			elif journal_entries:
					journal_entries.journal_id = x.bank_type.id
					journal_entries.date = x.expense_date
					for y in journal_entries.line_ids:
						y.partner_id = self.partner_id.id
						y.name = self.partner_id.name
						if y.debit ==0:
							y.credit=x.amount

						if y.credit ==0:
							y.debit=x.amount

			elif vendor_bill:
				vendor_bill.partner_id = x.vendor_name.id
				vendor_bill.reference = c.expense_type.name
				vendor_bill.date_invoice = x.expense_date
				vendor_bill.date_due = x.expense_date

				vendor_bill.invoice_line_ids.name = x.expense_type.name
				vendor_bill.invoice_line_ids.account_id = x.expense_type.haulage_journal.id
				vendor_bill.invoice_line_ids.price_unit = x.amount
				vendor_bill.invoice_line_ids.price_subtotal = x.amount







	@api.onchange('amount_total','tt_total_amount')
	def check_complete(self):
		if self.amount_total and self.tt_total_amount:
			if self.amount_total == self.tt_total_amount:
				self.is_complete = True
			else: 
				self.is_complete = False

	@api.onchange('partner_id')
	def get_partner_details(self):
		if self.partner_id:
			self.contact 		= self.partner_id.phone
			self.adress 		= self.partner_id.street
			self.incoterm 		= self.partner_id.incoterm
			self.payment_term_method = self.partner_id.payment_term
			self.forwarder 		= self.partner_id.forwarder
			self.clearing_agent = self.partner_id.clearing_agent
			self.currency_id 	= self.partner_id.currency

	@api.onchange('lc_costing_link','other_expense_link')
	def lc_costing_total(self):
		total 			= 0
		total_dollar 	= 0

		for x in self.lc_costing_link:
			total = total + x.total_amount
			total_dollar = total_dollar + x.amount
		for y in self.other_expense_link:
			total = total + y.amount
		self.amount_total_footer = total
		self.tt_total_amount = total_dollar
		if total > 0  and total_dollar > 0:
			self.per_dollar_cost = (total/total_dollar)

	@api.onchange('order_line','per_dollar_cost')
	def get_per_unit_cost(self):
		for x in self.order_line:
			x.pkr_unit_cost = self.per_dollar_cost * x.price_unit


	@api.onchange('order_line')
	def get_shippment_weight(self):
		nw_fn = 0
		gw_fn = 0
		cbm_fn = 0
		self.n_weight = nw_fn
		self.g_weight = gw_fn
		self.CBM = cbm_fn
		
		for x in self.order_line:
			nw_fn = nw_fn + (x.product_id.net_weight * x.carton)
			gw_fn = gw_fn + (x.product_id.gross_weight * x.carton)
			cbm_fn = cbm_fn + (x.product_id.cbm * x.carton)

		self.n_weight = nw_fn
		self.g_weight = gw_fn
		self.CBM = cbm_fn


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

class product_order_line_extension(models.Model): 
	_inherit = 'purchase.order.line'

	carton 			= fields.Float(string="CARTONS")
	last_purchase 	= fields.Float(string="Last Purchase")
	pkr_unit_cost 	= fields.Float(string="Per Unit Cost(PKR)")
	qty_hand 		= fields.Float(string="Qty on Hand", readonly=True)
	avg_unit_price 	= fields.Float(string="Avg Cost")
	avg_status 		= fields.Boolean(string="Average Price Status")

	@api.multi
	def unlink(self):
		product_details = self.env['product.product'].search([('default_code','=',self.order_id.product_id.default_code),('name','=',self.order_id.product_id.name)])
		for x in product_details.history_link:
			if x.po_no == self.order_id.name and x.po_qty == self.product_qty and x.unit_price == self.price_unit:
				x.unlink()
		super(product_order_line_extension,self).unlink()
		return True


	@api.onchange('product_id','product_qty','carton','price_unit','pkr_unit_cost')
	def get_values(self):
		stock_history = self.env['stock.history'].search([])
		qty_on_hand = 0
		value = 0
		avg = 0
		if self.product_id:
			for x in stock_history:
				if self.product_id == x.product_id:
					if self.order_id.date_order >= x.date:
						qty_on_hand = qty_on_hand + x.quantity
						value = value + x.inventory_value
			self.qty_hand = qty_on_hand
			if self.qty_hand:
				avg = (value + (self.product_qty * self.price_unit))/ (qty_on_hand + self.product_qty)
			self.avg_unit_price = avg
			
		if self.product_id:
			self.pkr_unit_cost = self.order_id.per_dollar_cost * self.price_unit


	@api.onchange('product_id')
	def get_last_purchase(self):
		self.last_purchase = 0
		self.price_unit = 0
		if self.product_id and self.order_id.partner_id:
			vendor_bill = self.env['account.invoice'].search([('type','=',"in_invoice")])
			for x in vendor_bill:
				if self.order_id.partner_id == x.partner_id:	
					for y  in x.invoice_line_ids:
						if self.product_id == y.product_id:
							print y.price_unit
							self.last_purchase = y.price_unit
							return


	@api.onchange('product_qty')
	def get_cartons(self):
		if self.product_qty and self.product_id:
			self.carton = self.product_qty / self.product_id.pcs_per_carton


	@api.onchange('carton')
	def get_quantity(self):
		if self.carton and self.product_id:
			self.product_qty = self.carton * self.product_id.pcs_per_carton

class shipping_document_attachment(models.Model):
	_name = 'shipping.document.attachment'

	doc_desc 			= fields.Char(string="Document Description")

	# doc_attachment 		= fields.Char(string="Attachment")
	doc_attachment 		= fields.Binary(string="Attachment")
	# doc_attachment 		= fields.many2many('ir.attachment', string="Attachments")
	shipping_doc_tree 	= fields.Many2one('purchase.order')




class lc_costing(models.Model):
	_name = 'lc.costing'

	tt_serial 			= fields.Char(string="TT Serial")
	tt_reference 		= fields.Char(string="TT Reference")
	date 				= fields.Date(string="Date", default=datetime.today())
	changer 			= fields.Many2one('money.changer',string="Money Changer")
	amount				= fields.Float(string="Amount")
	conversion_rate 	= fields.Float(string="Conversion Rate")
	bank_charges 		= fields.Float(string="Bank Charges")
	with_holding_tax 	= fields.Float(string="Withholding Amount")
	total_amount 		= fields.Float(string="Total Amount") 
	# lc_costing_tab 		= fields.Many2one('purchase.order')
	lc_costing_link_po 	= fields.Many2one('purchase.order')


# 	@api.onchange('tt')
# 	def count_total_tt_expense(self):
# 		if self.tt:
# 			self.amount 			= self.tt.amount
# 			self.conversion_rate 	= self.tt.conversion_rate
# 			self.bank_charges 		= self.tt.bank_charges
# 			self.with_holding_tax 	= self.tt.with_holding_tax
# 			self.total_amount 		= self.tt.total_amount + self.tt.with_holding_tax
# 			self.money_changer 		= self.tt.changer

class tt_lc_costing(models.Model):
	_name = 'tt.lc.costing'
	_rec_name = 'tt_serial'

	tt_serial 			= fields.Char(string="Serial No.", index=True, readonly=True)
	supplier_name 		= fields.Many2one('res.partner',string="Supplier")
	balance 			= fields.Float(string="Balance")
	tt_reference 		= fields.Char(string="Reference No.", required=True)
	amount				= fields.Float(string="Amount")
	amount_pkr 			= fields.Float(string="Amount Paid (PKR)", default=0)
	conversion_rate 	= fields.Float(string="Conversion Rate")
	bank_charges 		= fields.Float(string="Bank Charges")
	with_holding_tax 	= fields.Float(string="Withholding Amount")
	total_amount 		= fields.Float(string="Total Amount To be Paid (PKR)" , default=0) 
	changer 			= fields.Many2one('money.changer',string="Money Changer" ) 
	# po_no 				= fields.Many2one('purchase.order',string="PO No.")
	date 				= fields.Date(default=date.today())
	tt_lc_costing_link 	= fields.One2many('tt.lc.costing.line','tt_lc_costing_tree')
	tt_linked_po		= fields.One2many('tt.purchase.orders','tt_po_tree')
	state = fields.Selection([
	('draft', 'Draft'),
	('validate', 'Validate'),
	('done', 'Done'),
	('cancel', 'Cancel'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
	
	@api.multi
	def validate_tt(self):
		if self.amount_pkr and  self.total_amount:
			if self.amount_pkr != self.total_amount:
				raise UserError("Paid Amount and Pending Amount is not Equal")
			else:
				for x in self.tt_lc_costing_link:
					journal_entry = self.env['account.move'].search([])
					journal_entries_lines = self.env['account.move.line'].search([])
					if x.posted == False:
						create_journal_entry = journal_entry.create({
							'journal_id': x.journal.id,
							'date':self.date,
							'promo_id':self.id,
							'tt_serial':self.tt_serial,
							'ref':self.tt_reference,
							})
						create_debit = journal_entries_lines.create({
							'account_id':2,
							'partner_id':self.supplier_name.id,
							'name':"test",
							'debit':x.amount,
							'move_id':create_journal_entry.id
							})
						create_credit = journal_entries_lines.create({
							'account_id':3,
							'partner_id':self.supplier_name.id,
							'name':"test",
							'credit':x.amount,
							'move_id':create_journal_entry.id
						})
					x.posted = True
				self.state = "validate"

	@api.multi
	def cancel_tt(self):
		for x in self.tt_lc_costing_link:
			x.posted = False
		journal_entry = self.env['account.move'].search([('tt_serial','=',self.tt_serial)])
		for y in journal_entry:
			y.unlink()

		for y in self.tt_linked_po:
			order = self.env['purchase.order'].search([('id','=', y.po_no.id)])
			for x in order.lc_costing_link:
				if x.tt_serial == self.tt_po_tree.tt_serial:
					order.tt_total_amount = order.tt_total_amount - x.amount 
					x.unlink()
					y.posted = False

		self.state = "cancel"


	@api.multi
	def done_tt(self):
		if self.balance > 0:
			raise UserError('Balance is not Equal to 0')
		else:
			self.state = "done"

	@api.model
	def create(self, vals):	
		vals['tt_serial'] = self.env['ir.sequence'].next_by_code('tt.lc.costing')
		new_record = super(tt_lc_costing, self).create(vals)
		# if new_record.amount_pkr != new_record.total_amount:
		# 	raise UserError("Paid Amount and Pending Amount is not Equal")
		for x in new_record.tt_linked_po:
			if self.state == "validate":
				purchase_orders = self.env['purchase.order'].search([('id','=', x.po_no.id)])
				costing 		= self.env['lc.costing'].search([])
				if purchase_orders.tt_total_amount + x.amount > purchase_orders.amount_total:
					raise UserError('Punched TT Amount is Exceeding than PO Amount')
				else:
					amount_ratio 	= (x.amount/new_record.amount)
					with_hol 		= new_record.with_holding_tax * amount_ratio
					bank_charg 		= new_record.bank_charges * amount_ratio

					new_costing = costing.create({
							'tt_serial': new_record.tt_serial,
							'tt_reference': new_record.tt_reference,
							'date': new_record.date,
							'changer': new_record.changer.id,
							'amount':x.amount,
							'conversion_rate':new_record.conversion_rate,
							'bank_charges':bank_charg,
							'with_holding_tax':with_hol,
							})
					new_costing.lc_costing_link_po = purchase_orders.id
					x.posted = True
					purchase_orders.tt_total_amount = purchase_orders.tt_total_amount + x.amount 
			else:
				raise UserError('TT is not in Validated State, Delete the Linked Purchase Orders than Create TT')
		return new_record

	@api.multi
	def write(self, vals):	
		super(tt_lc_costing, self).write(vals)
		if self.amount_pkr != self.total_amount:
			raise ValidationError('Paid Amount and Pending Amount is not Equal')
		
		for x in self.tt_linked_po:
			purchase_orders = self.env['purchase.order'].search([('id','=', x.po_no.id)])
			costing 		= self.env['lc.costing'].search([])
			if x.posted != True:	
				if purchase_orders.tt_total_amount + x.amount > purchase_orders.amount_total:
					raise UserError('Punched TT Amount is Exceeding than PO Amount')
				elif self.state != "validate":
					raise UserError('TT is not in Validate State, You cannot Punch TT to any Purchase Order')
				else:
					amount_ratio 	= (x.amount/self.amount)
					with_hol 		= self.with_holding_tax * amount_ratio
					bank_charg 		= self.bank_charges * amount_ratio

					new_costing = costing.create({
						'tt_serial': self.tt_serial,
						'tt_reference': self.tt_reference,
						'date': self.date,
						'changer': self.changer.id,
						'amount':x.amount,
						'conversion_rate':self.conversion_rate,
						'bank_charges':bank_charg,
						'with_holding_tax':with_hol,
						'total_amount':(x.amount * self.conversion_rate) + bank_charg + with_hol
						})
					new_costing.lc_costing_link_po = purchase_orders.id
					x.posted = True
					purchase_orders.tt_total_amount = purchase_orders.tt_total_amount + x.amount 

		return True

	@api.onchange('amount','conversion_rate','bank_charges')
	def count_total_tt_costing(self):
		if self.amount and self.conversion_rate and self.bank_charges:
			self.total_amount = (self.amount * self.conversion_rate) + self.bank_charges


	@api.onchange('tt_lc_costing_link')
	def count_total_paid_amount(self):

		total_pkr		= 0
		total_withhold	= 0
		for x in self.tt_lc_costing_link:
			total_pkr = total_pkr + x.amount 
			total_withhold = total_withhold + x.with_holding 
		self.amount_pkr = total_pkr
		self.with_holding_tax = total_withhold

	@api.onchange('tt_linked_po','amount','balance')
	def count_total_linked_amount(self):
		total_pkr = 0
		for x in self.tt_linked_po:
			total_pkr = total_pkr + x.amount 
		self.balance = self.amount - total_pkr
		if self.balance < 0 and self.amount:
			raise UserError("Amount Is Not Balanced.")
		# elif self.balance < 0:
		# 	raise UserError("Amount Is Not Balanced.")





class tt_lc_costing_form(models.Model):
	_name = 'tt.lc.costing.line'

	journal 			= fields.Many2one('account.journal', string="Bank", required=True)
	cheque_no 			= fields.Char(string="To (Cheque No.)", required=True)
	cheque_no_to 		= fields.Char(string="From (Cheque No.)", required=True)
	with_holding 		= fields.Float(string="Withholding Amount", required=True)
	amount				= fields.Float(string="Amount (PKR)",required=True)
	name 				= fields.Many2one('purchase.order',string="PO No.")
	tt_lc_costing_tree 	= fields.Many2one('tt.lc.costing')
	posted 				= fields.Boolean(readonly=True)

class tt_purchase_orders(models.Model):
	_name = 'tt.purchase.orders'

	amount		= fields.Float(string="Amount",required=True)
	po_no 		= fields.Many2one('purchase.order',string="PO No.", required=True)
	posted 		= fields.Boolean(string="Posted", readonly=True)
	tt_po_tree 	= fields.Many2one('tt.lc.costing')


	@api.multi
	def unlink(self):
		order = self.env['purchase.order'].search([('id','=', self.po_no.id)])
		for x in order.lc_costing_link:
			if x.tt_serial == self.tt_po_tree.tt_serial and x.amount == self.amount:
				order.tt_total_amount = order.tt_total_amount - x.amount 
				x.unlink()


		super(tt_purchase_orders,self).unlink()

		return True

class account_journal_extension(models.Model):
	_inherit = 'account.journal'

	with_holding_rate = fields.Float(string="Withholding Rate")


class other_expense(models.Model):
	_name = 'other.expense'


	expense_type 		= fields.Many2one('haulage.expense',string="Expense Type")
	vendor_name 		= fields.Many2one('res.partner', string="Vendor Name")
	amount 				= fields.Float(string="Amount")
	bank_type 			= fields.Many2one('account.journal', string="Bank")
	expense_date 		= fields.Date(string="Date", default=date.today())
	description 		= fields.Char(string="Reference")
	check_no  			= fields.Char(string="Check No.")
	status  			= fields.Boolean(string="Status")
	other_expense_tree 	= fields.Many2one('purchase.order') 

	@api.multi
	def unlink(self):
		super(other_expense,self).unlink()
		pricelist = self.env['account.move'].search([('promo_id','=', self.id)])
		if pricelist:
			pricelist.unlink()

		return True


class haulage_expense(models.Model):
	_name ='haulage.expense'

	name 	 			= fields.Char(string="Expense Name", required=True)
	haulage_journal 	= fields.Many2one('account.account', required=True, string="Expense Account")	




class money_changer(models.Model):
	_name ='money.changer'

	name 	 		= fields.Char(string="Name")
	adress 			= fields.Char(string="Address")	
	tele_phone 		= fields.Char(string="Telephone No.")	



class shipping_line(models.Model):
	_name = 'shipping.line'

	name = fields.Char(string="Shipping Line", required=True)

class loading_port(models.Model):
	_name = 'loading.port'

	name = fields.Char(string="POL", required=True)

class destination_port(models.Model):
	_name = 'destination.port'

	name = fields.Char(string="POD", required=True)

	