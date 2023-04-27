# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

XML_IDS = [
    "provision_on_order",
    "no_backorder",
    "warning_supplier_break",
]


def pre_init_hook(cr):
    # move xml_ids from sale_specific to alc_sale_exception
    openupgrade.rename_xmlids(
        cr,
        [
            (
                f"specific_sale.{xml_id}",
                f"alc_sale_exception_product_availability.{xml_id}",
            )
            for xml_id in XML_IDS
        ],
    )
