# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Reception Rank Release Channel",
    "description": """
        Alcyon: Higher rank for reception of waiting product into a release channel

        If an incoming product is into a deliveries waiting for its availability,
        the rank of the reception is increased to be higher if the delivery is
        into a release channel. (x * 1000000 where x is the number of release channel
        waiting for the product)
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_stock_reception_rank",
        "stock_release_channel",
    ],
    "data": [],
    "demo": [],
}
