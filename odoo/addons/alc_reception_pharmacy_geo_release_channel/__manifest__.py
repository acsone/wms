# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Reception Pharmacy Geo Release Channel",
    "description": """
        Alcyon: Glue module between alc_reception_pharmacy
                and stock_release_channel_geoengine.

        Adapt the computation logic to know if a customer is delivered by alcyon
        when receiving a colis from the pharmacy
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_partner_delivered_by_alcyon",
        "alc_reception_pharmacy",
        # OCA
        "delivery_carrier_partner",
        "stock_release_channel_delivery",
        "stock_release_channel_geoengine",
    ],
    "data": [],
    "demo": [],
    "installable": True,
}
