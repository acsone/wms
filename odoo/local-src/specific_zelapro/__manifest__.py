# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Zelapro module for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Okia SPRL',
    'license': 'AGPL-3',
    'category': 'Other',
    'description': """
    Specific module for Zelapro
    """,
    'depends': [
        'specific_purchase',
        'specific_stock',
        'product_additional',
        'import_manager',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # SQL views
        'sql_views/zelapro_export_cadencier_header.sql',
        'sql_views/zelapro_export_cadencier.sql',
        'sql_views/zelapro_export_contacts.sql',
        'sql_views/zelapro_export_lot_moves.sql',
        'sql_views/zelapro_export_lots.sql',
        'sql_views/zelapro_export_products.sql',
        'sql_views/zelapro_export_promotions.sql',
        'sql_views/zelapro_export_stock_moves.sql',
        'sql_views/zelapro_export_suppliers.sql',

        # Views
        'views/zelapro_export.xml',
        'views/zelapro_config_settings.xml',
        'views/product_category.xml',
        'views/product_template.xml',
        'wizard/zelapro_export_wizard.xml',
        'views/activity_base_testing.xml',
        'views/import_config_settings.xml',

        # Data
        'data/ir_config_parameter.xml',
        'data/zelapro_export.xml',
        'data/ir_cron.xml',
        'data/activity_based_costing.xml',
        'data/import_file.xml',

        # Security
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
