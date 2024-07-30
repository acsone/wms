# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Processing Finalizer Exclude Logiweb",
    "description": """
        exclude logiweb sale orders from automatic cancellation""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Custom
        "alc_sale_processing_finalizer",
    ],
    "demo": [],
    "installable": True,
}
