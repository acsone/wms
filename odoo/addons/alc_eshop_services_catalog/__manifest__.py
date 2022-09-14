# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Catalog Webservice",
    "description": """Alcyon: Catalog Webservices""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "authenticated_partner_mixin",
        "sale",
        "alc_partner_type",
        "product_brand",
        "standard_service_mixin",
        "paginated_service_mixin",
    ],
    "demo": [],
    'installable': False
}