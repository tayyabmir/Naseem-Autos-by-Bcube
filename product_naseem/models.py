# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
import datetime
from datetime import datetime,date,timedelta,time

class product_template_extension(models.Model): 
    _inherit = 'product.template' 
    list_price         = fields.Float (string = "List Price")
    default_code       = fields.Char  (string = "Product Id" )
    hs_code            = fields.Char  (string = "HS Code")
    minimum_level      = fields.Float (string = "Minimum Level")
    maximum_level      = fields.Float (string = "Maximum Level")
    foc                = fields.Boolean('Free of Cost')
    qty_per_carton     = fields.Integer (string = "Qty per Carton")
    net_weight         = fields.Float(string ="Net Weight")
    gross_weight       = fields.Float(string = "Gross Weight")
    cbm                = fields.Float(string = "CBM")
    # list_price_own            = fields.Integer('List Price', readonly = True)
    # level_1                = fields.Integer('Price Level 1', readonly = True)
    # level_2                = fields.Integer('Price Level 2', readonly = True)
    # level_3                = fields.Integer('Price Level 3', readonly = True)
    
    type = fields.Selection([
        ('consu','Consumable'),
        ('service','Service'),
        ('product','Stockable')], string='Product Type', default='product', required=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A consumable product, on the other hand, is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')


class uom_default(models.Model):
    _inherit = 'product.uom'

    uom_type =  fields.Selection([('bigger','Bigger than the reference Unit of Measure'),
                                      ('reference','Reference Unit of Measure for this category'),
                                      ('smaller','Smaller than the reference Unit of Measure')],'Type', required=1, default = 'bigger')

    category_id = fields.Many2one(
        'product.uom.categ', 'Category', required=True, ondelete='cascade', default = 1,
        help="Conversion between Units of Measure can only occur if they belong to the same category. The conversion will be made based on the ratios.")
    factor_inv = fields.Float(string = "No of Units per Carton")

class product_history(models.Model):
  _name = 'product.history'
  date        = fields.Date(string="Date")
  qty         = fields.Float(string="Quantity")
  # carton      = fields.Float(string="Carton")
  unit_price  = fields.Float(string="Unit Price")
  pre_qty     = fields.Float(string="Previous Quantity")
  # pre_carton  = fields.Float(string="Previous Carton")
  adjustment  = fields.Float(string="Adjustment")
  net         = fields.Float(string="Net")
  pre_price   = fields.Float(string="Previous Purchase Price")
  avg_price   = fields.Float(string="Average Price")
  po_qty      = fields.Float(string="PO Quantity")
  po_no       = fields.Char(string="PO No.")
  history_id  = fields.Many2one('product.product')

  # @api.onchange('adjustment')
  # def update_average(self):
  #   if self.adjustment:
  #     # forecast_value = self.env['report.stock.forecast'].search([('product_id','=',self.history_id.product_id.id)])
  #     new_net = self.net - self.adjustment
  #     old_avg_price = new_net * self.history_id.average_cost
  #     new_avg_price = self.po_qty * self.unit_price 
  #     calculate_average = (old_avg_price + new_avg_price) / (self.po_qty + new_net)
  #     self.avg_price = calculate_average



class product_extension(models.Model): 
    _inherit = 'product.product' 
  
    
    lst_price          = fields.Float (string = "List Price")
    default_code       = fields.Char  (string = "Product Id", required=True )
    hs_code            = fields.Char  (string = "HS Code")
    minimum_level      = fields.Float (string = "Minimum Level")
    maximum_level      = fields.Float (string = "Maximum Level")
    foc                = fields.Boolean(string="Free of Cost")
    list_price_own     = fields.Integer(string="List Price", readonly="1")
    level_1            = fields.Integer('Price Level 1', readonly = True)
    level_2            = fields.Integer('Price Level 2', readonly = True)
    level_3            = fields.Integer('Price Level 3', readonly = True)
    prod_desc          = fields.Char(string="Product Descripion")
    inventory_prod     = fields.Boolean(string="Product Descripion")
    pcs_per_carton     = fields.Integer('PC(s) Per Carton')
    history_link       = fields.One2many('product.history','history_id')
    previouse_purchase = fields.Float(string="Previous Purchase", default=0)
    previouse_qty      = fields.Float(string="Previous Qty", default=0)
    average_cost       = fields.Float(string="Average Cost", default=0)
    # previouse_carton   = fields.Float(string="Previous Carton", default=0)

    uom                 = fields.Selection([('pcs', 'PC(s)'),
                            ('roll','ROLL(s)'),
                            ],string = "UOM")    

    
    type = fields.Selection([
        ('consu','Consumable'),
        ('service','Service'),
        ('product','Stockable')], string='Product Type', default='product', required=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A consumable product, on the other hand, is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')


    @api.onchange('maximum_level')
    def _onchange_maximum_level(self):
      if self.maximum_level < self.minimum_level:
        raise Warning('Maximum stock must be greater than minimum level')


    @api.model
    @api.constrains()
    def create(self, vals):
      new_record = super(product_extension, self).create(vals)
      create_reorder = self.env['stock.warehouse.orderpoint'].create({
        'product_id': new_record.id,
        'product_max_qty':new_record.maximum_level,
        'product_min_qty': new_record.minimum_level
        })

      all_products = self.env['product.product'].search([('id','!=',new_record.id)])
      list_codes = []
      for x in all_products:
        list_codes.append(x.default_code)
      if new_record.default_code in list_codes:
        raise ValidationError('Product with this Code already exist')

      
      # new_record.hs_code       = new_record.product_tmpl_id.default_code
      # new_record.maximum_level = new_record.product_tmpl_id.maximum_level
      # new_record.minimum_level = new_record.product_tmpl_id.minimum_level
      



      return new_record

    @api.multi
    def write(self, vals):
      super(product_extension, self).write(vals)
      for x in self.orderpoint_ids:

        x.product_max_qty = self.maximum_level
        x.product_min_qty = self.minimum_level

      return True

class attribute_category(models.Model):
    _inherit = 'product.attribute.value'

    category_id = fields.Many2many('product.category', string = "Category" , required = True)

class attribute_line(models.Model):
    _inherit = 'product.attribute.line'

    value_ids = fields.Many2many('product.attribute.value')


class product_category_extension(models.Model):
    _inherit = 'product.category'

    @api.model
    def create(self, vals):
      new_record = super(product_category_extension, self).create(vals)
      new_record.property_valuation ="real_time"
      new_record.property_cost_method ="average"
      return new_record



class addrerss_contacts(models.Model): 
    _name = 'address.contacts'

    customer_name = fields.Char(string="Contact Name", required= True)
    job_position = fields.Char(string="Job Position", placeholder="eg. Manger")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    address = fields.Char(string="Address")
    invoice_address = fields.Char(string="Invoice Address")
    shipping_address = fields.Char(string="Shipping Address")
    
    title = fields.Many2one('res.partner.title', string="Title");

    address_contact_id = fields.Many2one('res.partner')


# Add Wizard
class wizard_tree(models.TransientModel):
  _name="wizard.tree"

  product = fields.Many2one("product.product",string="Product",required =True,readonly =True)
  qty     = fields.Float(string="Quantity")
  carton  = fields.Float(string="Carton")

  prod_name = fields.Many2one("wizard.class")

  @api.onchange('qty')
  def get_carton(self):
    if self.qty:
      self.carton = self.qty / self.product.pcs_per_carton 

  @api.onchange('carton')
  def get_qty(self):
    if self.carton:
      self.qty = self.carton * self.product.pcs_per_carton


class wizard_class(models.TransientModel):
    _name = "wizard.class"

    product_tree  = fields.One2many("wizard.tree","prod_name")
    category      = fields.Many2one('product.category')
    sale_boolean  = fields.Boolean(string="SO/PO")

    @api.onchange('category')
    def generate_products(self):
      new_data = []
      if self.category:
        all_products = self.env['product.product'].search([])
        all_product_qty = self.env['stock.change.product.qty'].search([])
        print self.category.id 
        for x in all_products:
          if x.categ_id.id == self.category.id:
            data = self._prepare_line_items(x.id, self.id)
            new_data.append((0,0, data))
            self.product_tree = new_data

    def _prepare_line_items(self, product_id, current_id):
      res = {
      'product':product_id,
      'wizard.id':current_id
      }
      return res
    
    @api.multi
    def generate(self):
      active_class = self.env['sale.order'].browse(self._context.get('active_id'))
      if active_class:
        for x in self.product_tree:
          if x.qty >0:
            generate_so_line= active_class.order_line.create({
              'product_id': x.product.id,
              'product_uom_qty':x.qty,
              'carton': x.carton,
              'order_id': active_class.id
              })
          for y in active_class.order_line:
            if y.product_id.product_tmpl_id.qty_per_carton>0:
              y.carton = y.product_uom_qty/y.product_id.product_tmpl_id.qty_per_carton
    @api.multi
    def generate_purchase(self):
      active_class_purchase = self.env['purchase.order'].browse(self._context.get('active_id'))
      if active_class_purchase:
        for x in self.product_tree:
          if x.qty >0:
            if x.product.prod_desc:
              desc = x.product.prod_desc
            else:
              desc = x.product.name
            generate_po_line= active_class_purchase.order_line.create({
              'product_id': x.product.id,
              'product_uom_qty':x.qty,
              # 'uom':x.product.uom,
              'product_uom':x.qty,
              'product_qty':x.qty,
              'price_unit':0,
              'name':desc,
              'date_planned':date.today(),
              'order_id': active_class_purchase.id
              })
            print "xxxxxxxxxxxxxxxxXXXXxx"
            print x.product.name
            print "yyYYYYYYYYyyyyyYYYYY"
          for y in active_class_purchase.order_line:
            if y.product_id.product_tmpl_id.qty_per_carton>0:
              y.carton = y.product_uom_qty/y.product_id.product_tmpl_id.qty_per_carton

 
class add_wizard(models.Model):
  _inherit= "sale.order"

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

class sale_order_extension(models.Model):
  _inherit = "sale.order.line"

  carton = fields.Float(string="Carton")


#   @api.onchange('product_uom_qty')
#   def generate_carton_value(self):

#     if self.product_id.product_tmpl_id.qty_per_carton>0:
#       self.carton = self.product_uom_qty/self.product_id.product_tmpl_id.qty_per_carton
      

#   @api.onchange('carton')
#   def generate_units(self):

#     if self.product_id.product_tmpl_id.qty_per_carton>0:
      
#       self.product_uom_qty = self.carton * self.product_id.product_tmpl_id.qty_per_carton


class credit_limit(models.Model):
  _inherit = "account.invoice"

  balance = fields.Float(string="Balance")
  

  @api.multi
  @api.constrains()
  def _check_total(self,credit,credit_limit):
    if credit > credit_limit:
      raise ValidationError('Amount is exceeding credit limit')

  @api.model
  def create(self, vals):
    
    new_record = super(credit_limit, self).create(vals)
    credit1 = new_record.partner_id.credit + new_record.amount_total
    credit_limit1 = new_record.partner_id.credit_limit 
    self._check_total(credit1,credit_limit1)

    return new_record



