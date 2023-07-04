# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Initialize xml ids from production database entries (migration v16)."""

    openupgrade.add_xmlid(
        cr,
        "alc_stock_storage_type_sequence_condition",
        "condition_besoin_reassort",
        "stock.storage.location.sequence.cond",
        1,
    )
    openupgrade.add_xmlid(
        cr,
        "alc_stock_storage_type_sequence_condition",
        "condition_lot_en_stock",
        "stock.storage.location.sequence.cond",
        2,
    )
    openupgrade.add_xmlid(
        cr,
        "alc_stock_storage_type_sequence_condition",
        "condition_ancien_lot",
        "stock.storage.location.sequence.cond",
        3,
    )
    openupgrade.add_xmlid(
        cr,
        "alc_stock_storage_type_sequence_condition",
        "condition_deja_stock",
        "stock.storage.location.sequence.cond",
        4,
    )
