{
    'name': 'Custom Inventory Label',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Custom labels for inventory management',
    'description': """
        This module provides custom labels for stock move operations, 
        including product and material details.
    """,
    'license': 'LGPL-3',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_views.xml',
        'reports/report_inventory_label.xml',
        'security/ir.model.access.csv',
        'views/ir_actions_server.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
