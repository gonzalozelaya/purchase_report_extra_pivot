# -*- coding: utf-8 -*-
{
    'name': "purchase_report_extra_pivot",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "OutsourceArg",
    'website': "https://www.outsourcearg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    'data': [
        'security/ir.model.access.csv',
        'views/requisition_dashboard_views.xml',
    ],
    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'stock','purchase_requisition', 'stock'],  # Agrega 'purchase' y otros módulos necesarios,
}
