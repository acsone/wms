# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Rma Operation Return Location",
    "description": """
        This addon allows the RMA manager to specify, for certain operations, a specific
         return location different from the one proposed in the return wizards.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "rma_sale",
    ],
    "data": ["views/rma_operation.xml"],
    "demo": [],
}
