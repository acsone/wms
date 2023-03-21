# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Delivery Rounds Blocking Unavailable Product",
    "description": """
        Alcyon: Block delivery of unavailable products when the unavailability
        has been announced on the SO""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_delivery_rounds_assign_blocking",
        "procurement_sale"  # TODO: partially replaced by alc_sale_product_qty_unavailable
    ],
    "data": [],
    "demo": [],
    "installable": False,
}
