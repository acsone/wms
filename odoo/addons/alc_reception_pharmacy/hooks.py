# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved fields from specific_stock
    openupgrade.update_module_moved_fields(
        cr,
        "reception.pharmacy",
        ["date", "product_id", "line_ids", "state"],
        "specific_stock",
        "alc_reception_pharmacy",
    )

    openupgrade.update_module_moved_fields(
        cr,
        "reception.pharmacy.line",
        [
            "wizard_id",
            "customer_id",
            "bin_id",
            "product_qty",
            "reception_move_id",
            "procurement_id",
            "partner_shipping_id",
        ],
        "specific_stock",
        "alc_reception_pharmacy",
    )

    openupgrade.rename_xmlids(
        cr,
        [
            (
                "specific_stock.product_colis_souverain",
                "alc_reception_pharmacy.product_colis_souverain",
            ),
            (
                "specific_stock.product_colis_souverain_frigo",
                "alc_reception_pharmacy.product_colis_souverain_frigo",
            ),
            (
                "specific_stock.seq_lot_pharmacy",
                "alc_reception_pharmacy.seq_lot_pharmacy",
            ),
        ],
    )
