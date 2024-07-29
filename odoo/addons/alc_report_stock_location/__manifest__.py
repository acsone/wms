# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Location Report",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Warehouse",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # OCA
        "stock_location_zone",
        # Others
        "stock",
        # fmt: on
    ],
    "data": [
        "views/report_location_barcode.xml",
        "views/paperformat.xml",
        "views/paperformat_medoc.xml",
    ],
    "installable": True,
}
