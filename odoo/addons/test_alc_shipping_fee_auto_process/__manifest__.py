# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Test: Alcyon Shipping Fee Auto Process",
    "description": """Test shipping fee logic in case of automatic release channel
    with auto process shipments.
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "stock_release_channel_shipment_advice_deliver",
        # Alcyon/Delivery
        "alc_shipping_fee",
    ],
    "application": False,
    "data": [],
    "demo": [],
}
