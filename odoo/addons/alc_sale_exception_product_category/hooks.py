# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

XML_IDS = [
    "no_food_allowed",
    "no_medoc_allowed",
    "no_medoc_cascade_import",
    "no_medoc_veterinary_belge",
    "no_medoc_human",
    "no_medoc_vet_stup",
    "no_medoc_vet_stupIII",
    "no_medoc_belgium_only",
    "no_veterinary_product",
    "no_psychotropic_by_phone",
    "no_stupefiant_vet_by_phone",
    "warning_psychotropic",
    "warning_stupefiant_vet",
    "warning_cascade_import",
    "warning_human_medoc",
    "order_amount_material_maximum",
]


def pre_init_hook(cr):
    # move xml_ids from sale_specific to alc_sale_exception
    openupgrade.rename_xmlids(
        cr,
        [
            (f"specific_sale.{xml_id}", f"alc_sale_exception.{xml_id}")
            for xml_id in XML_IDS
        ],
    )
