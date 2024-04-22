# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Location Report",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Warehouse",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock", "stock_location_zone"],
    "data": [
        "views/report_location_barcode.xml",
        "views/paperformat.xml",
        "views/report_location_barcode_medoc.xml",
        "views/paperformat_medoc.xml",
    ],
    "installable": True,
}
