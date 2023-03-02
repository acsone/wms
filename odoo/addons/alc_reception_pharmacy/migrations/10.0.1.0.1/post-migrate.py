# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Update Colis souverain/souverain frigo with right category")
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    colis_souverain_category_id = env.ref(
        "specific_data.product_categ_colis_souverain"
    ).id
    colis_souverain_id = env.ref("alc_reception_pharmacy.product_colis_souverain").id
    colis_souverain_tmpl_id = colis_souverain_id.product_tmpl_id.id
    colis_souverain_frigo_id = env.ref(
        "alc_reception_pharmacy.product_colis_souverain_frigo"
    ).id
    colis_souverain_tmpl_id = colis_souverain_frigo_id.product_tmpl_id.id

    cr.execute(
        """
        UPDATE
            product_product
            SET categ_id = %(category_id)s
        WHERE id in %(product_ids)s;
        """,
        {
            "category_id": colis_souverain_category_id,
            "product_ids": [colis_souverain_id, colis_souverain_frigo_id],
        },
    )

    cr.execute(
        """
        UPDATE
            product_template
            SET is_colis_souverain = True
        WHERE id in %(product_tmpl_ids)s;
        """,
        {"product_tmpl_ids": [colis_souverain_tmpl_id, colis_souverain_tmpl_id]},
    )
