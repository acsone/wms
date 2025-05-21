# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Packing Parcels Split",
    "summary": """Alcyon: Generate as many packages as the number of parcels specified on the package type if requested by the package type on put in pack""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "shopfloor_packing",
        # Alcyon
        "alc_delivery_package_type_number_parcels_split",
    ],
    "data": [],
    "demo": [],
}
