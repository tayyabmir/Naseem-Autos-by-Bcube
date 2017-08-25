# -*- coding: utf-8 -*-
{
    'name': "pricelists_extension",

    'summary': """
        Simplifying PriceLists""",

    'description': """
        Simplifying PriceLists
    """,

    'author': "BCUBE",
    'website': "bcbue.pk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','base','sale','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
    ],

}