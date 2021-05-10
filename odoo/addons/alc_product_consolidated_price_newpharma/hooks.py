# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api
from odoo.osv.expression import AND, OR

_logger = logging.getLogger(__name__)


def _initialize_product_assortment_filter(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Initialize Newpharam product assortment filter")
    assortment_filter = env.ref(
        "alc_product_consolidated_price_newpharma.newpharma_product_assortment_filter"
    )
    supplier_ids_to_exclude = (
        env["res.partner"]
        .search(
            [
                ("supplier", "=", True),
                (
                    "ref",
                    "in",
                    [
                        "60425",  # agora_sana
                        "61645",  # ASP International
                        "101895",  # Finest Petfood
                        "77020",  # Original Process
                        "77640",  # Phytovet
                    ],
                ),
            ]
        )
        .ids
    )
    domain = AND(
        [
            [("web_published", "=", True)],
            OR(
                [
                    [
                        (
                            "categ_id",
                            "child_of",
                            env.ref("specific_data.product_categ_materiel").id,
                        )
                    ],
                    [
                        (
                            "categ_id",
                            "child_of",
                            env.ref("specific_data.product_categ_ali").id,
                        )
                    ],
                    [
                        (
                            "categ_id",
                            "child_of",
                            env.ref("specific_data.product_categ_vet_belges").id,
                        )
                    ],
                    [
                        (
                            "categ_id",
                            "child_of",
                            env.ref("specific_data.product_categ_parapharmacie").id,
                        )
                    ],
                ]
            ),
            [("supplier_id", "not in", supplier_ids_to_exclude)],
            [
                ("name", "not ilike", "pvd "),
                ("name", "not ilike", "vetessentials"),
                ("name", "not ilike", "promo"),
                ("name", "not ilike", "sticker"),
            ],
        ]
    )
    assortment_filter.domain = str(domain)


def post_init_hook(cr, registry):
    _initialize_product_assortment_filter(cr)
