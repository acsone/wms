# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc All",
    "description": """
        Alcyon Odoo App""",
    "version": "16.0.2.0.22",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "server_environment",
        "server_environment_ir_config_parameter",
        "web_environment_ribbon",
        "web_chatter_position",
        "web_refresher",
        "web_search_with_and",
        "web_sheet_full_width",
        "web_tree_many2one_clickable",
        # C2C
        "attachment_s3",
        # ALC
        "alc_app_framework",
        "alc_app_invoicing",
        "alc_app_order_picking",
        "alc_app_purchase",
        "alc_app_putaway",
        "alc_app_receipt",
        "alc_app_return",
        "alc_app_sale",
        "stock_scrap_location_default",
        "alc_partner_message_subscribe",
        "alc_partner_name",
        # TO BE REMOVED
        "base_report_to_printer",
    ],
    "application": True,
    "data": [
        "security/sale_order.xml",
        "security/product_state.xml",
        "security/res_groups.xml",
        "views/product_packaging.xml",
        "views/product_template.xml",
        "views/res_partner.xml",
        "data/ir_config_parameter.xml",
        "data/res_company.xml",
    ],
    "demo": [],
}
