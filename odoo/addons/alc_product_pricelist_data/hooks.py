# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Moved xml_id from specific_data
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "specific_data.product_pricelist_pb1",
                "alc_product_pricelist_data.product_pricelist_pb1",
            ),
            (
                "specific_data.product_pricelist_pb2",
                "alc_product_pricelist_data.product_pricelist_pb2",
            ),
        ],
    )
