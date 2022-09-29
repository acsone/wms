# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Quick Create: Pricelist Discount",
    "description": """Sale Quick Create: Pricelist Discount
        Glue module that duplicates view changes necessary to get discount
        onchanges to be applied.""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["sale_quick_create", "pricelist_discount"],
    "data": ["views/sale_order_line.xml"],
    "demo": [],
    "installable": False,
}
