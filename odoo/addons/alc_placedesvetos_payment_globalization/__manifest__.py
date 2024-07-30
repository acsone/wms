# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Place des Vetos Payment Globalization",
    "description": """
        Allows payment globalization for placesdesvetos
        Adds a dedicated menu entry to help globalize payment for Place des Vetos
        Provides a specialized wizard with prefilled values and generating
        the required documents to help the accounting on the Place des Vetos side
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_account_payment_globalization",
        "alc_placedesvetos",
        # OCA
        "report_csv",
    ],
    "data": [
        "security/alc_placedesvetos_payment_globalization.xml",
        "wizards/alc_placedesvetos_payment_globalization.xml",
        "reports/report.xml",
    ],
    "demo": [],
}
