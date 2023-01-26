# Copyright 2017 Julien Coux (Camptocamp)
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product additional for Alcyon",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Product",
    "depends": [
        # Odoo
        "product",
        "product_expiry",
        "stock",
        "sale",
        "purchase",
        # OCA
        "stock_available_immediately",
        # ALC
        "alc_pricelist_discount",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        "views/purchase_order.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["types-python-dateutil"]},
}
