# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Cluster Picking Printing",
    "description": """
        Alcyon: Automatic printing of product labels and packages labels into
        the cluster picking process""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_shopfloor_product_print_label",
        # OCA
        "base_report_to_label_printer",
        "shopfloor_packing",
        "stock_storage_type",
        # Others
        "delivery",
    ],
    "data": ["views/shopfloor_menu.xml"],
    "demo": [],
}
