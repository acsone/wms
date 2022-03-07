# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Magento API Facade",
    "description": """Alcyon: Magento API Facade""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_eshop",  # bring all fields
        "alc_eshop_services_catalog",
        "alc_eshop_services_deliveries",
        # TODO: cart service
    ],
    "demo": [],
    "external_dependencies": {"python": ["xmltodict", "dicttoxml"]},
}
