# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# this module should not exist: for humans product, qty_remains_to_deliver
# should always be 0, same as qty_unavailable
# so it should be replaced by a module, e.g. procurement_sale_human
# currently it works in backend by modifying the view filter
# however, this relies on a hack: it expects human product to be configured as services
# but this is not enforced, and some products are thus badly configured.

{
    "name": "Alc Eshop Sale Cart Product Unavailable: Pharmacy Products",
    "description": """
        Alcyon: Unavailable qty announcement for pharmacy products""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_eshop_schema_sale_product_unavailable",
        "alc_product_pharmacy",
    ],
    "data": [],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}
