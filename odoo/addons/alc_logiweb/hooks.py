# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api
from odoo.osv.expression import AND, OR

_logger = logging.getLogger(__name__)


def _initialize_product_assortment_filter(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Initialize Newpharam product assortment filter")
    assortment_filter = env.ref("alc_logiweb.logiweb_product_assortment_filter")
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
    domain = [
        ("type", "=", "product"),
        ("active", "=", True),
        ("sale_ok", "=", True),
        ("default_code", "!=", False),
    ]
    domain = AND(
        [
            domain,
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
                            env.ref("specific_data.product_categ_parapharmacie").id,
                        )
                    ],
                ]
            ),
            [("supplier_id", "not in", supplier_ids_to_exclude)],
        ]
    )
    assortment_filter.domain = str(domain)


def post_init_hook(cr, registry):
    _initialize_product_assortment_filter(cr)
