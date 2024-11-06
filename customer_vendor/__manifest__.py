{
    'name': 'Customer/Vendor Dropdown Filter',
    'version': '1.0',
    'category': 'Contacts',
    'summary': 'Filter partners by customer/vendor type across Odoo.',
    'description': """
    Adds a dropdown in the contact form to select between Customer, Vendor, or Both.
    Automatically filters the contact selection based on customer/vendor type in models like Sales, Purchases, and Accounting.
    """,
    'depends': ['base', 'sale', 'purchase', 'account'],
    'data': [
        'views/res_partner_views.xml',
        'views/model_view_inherit.xml',
    ],
    'installable': True,
    'application': False,
}
