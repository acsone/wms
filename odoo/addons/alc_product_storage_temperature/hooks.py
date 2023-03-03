# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.update_module_moved_models(
        cr,
        "product.storage.temperature",
        "specific_product",
        "alc_product_storage_temperature",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "product.storage.temperature",
        ["name", "temperature"],
        "specific_product",
        "alc_product_storage_temperature",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "product.template",
        ["storage_temperature_id"],
        "specific_product",
        "alc_product_storage_temperature",
    )
