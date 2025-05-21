# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Delivery Package Type Number Parcels Split",
    "summary": """Alcyon: Add option to create as many pack as the number of parcels specified on the selected package type on put in pack. Products are 'equaly' and 'randomly'  distributed among the various packs.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "delivery_package_type_number_parcels",
    ],
    "data": [
        "views/stock_package_type.xml",
    ],
    "demo": [],
}
