# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
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
