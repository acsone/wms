# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Alc Supplier Purchase Manager Account",
    "description": """
        ALcyon: Hide puchase managers on view if the partner is not a supplier
                based on supplier_rank""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_supplier_purchase_manager",
        # Others
        "account",
    ],
    "data": ["views/res_partner_views.xml"],
    "demo": [],
    "installable": True,
}
