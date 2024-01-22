# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Alc Supplier Purchase Manager",
    "description": """
        ALcyon: Define puchase manager on supplier""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",  # MUST BE LGPL since will be mixed with helpdesk
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["purchase", "purchase_stock"],
    "data": ["views/res_partner_views.xml", "views/purchase_order.xml"],
    "demo": [],
    "installable": True,
}
