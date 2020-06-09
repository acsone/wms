# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _initialize_product_assortment_filter(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Initialize b2c product assortment filter")
    assortment_filter = env.ref("alc_b2c_connector.b2c_product_assortment_filter")
    domain = [
        ("type", "=", "product"),
        ("active", "=", True),
        ("sale_ok", "=", True),
        ("default_code", "!=", False),
    ]
    domain.extend(
        [
            "!",
            ("categ_id", "child_of", env.ref("specific_data.product_categ_humain").id),
        ]
    )
    domain.extend(
        [
            "!",
            (
                "categ_id",
                "child_of",
                env.ref("specific_data.product_categ_vet_belges").id,
            ),
        ]
    )
    domain.extend(
        [
            "!",
            (
                "categ_id",
                "child_of",
                env.ref("specific_data.product_categ_importation").id,
            ),
        ]
    )

    assortment_filter.domain = str(domain)


def post_init_hook(cr, registry):
    _initialize_product_assortment_filter(cr)
