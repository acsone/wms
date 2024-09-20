# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Set the order on pakage type categories

    categories = env["stock.package.type.category"].search([])
    for category in categories:
        if category.name == "Médicaments":
            category.write(
                {
                    "show_in_shipment_advice_report": True,
                    "sequence_in_shipment_advice_report": 1,
                }
            )
        if category.name == "Frigo":
            category.write(
                {
                    "show_in_shipment_advice_report": True,
                    "sequence_in_shipment_advice_report": 2,
                }
            )
        if category.name == "Aliments":
            category.write(
                {
                    "show_in_shipment_advice_report": True,
                    "sequence_in_shipment_advice_report": 3,
                }
            )
        if category.name == "Matériel":
            category.write(
                {
                    "show_in_shipment_advice_report": True,
                    "sequence_in_shipment_advice_report": 4,
                }
            )
