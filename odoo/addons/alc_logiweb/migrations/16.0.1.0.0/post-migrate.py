# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api
from odoo.osv.expression import AND, OR

_logger = logging.getLogger(__name__)


def _initialize_product_assortment_filter(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Initialize Logiweb product assortment filter")
    assortment_filter = env.ref("alc_logiweb.logiweb_product_assortment_filter")
    supplier_ids_to_exclude = (
        env["res.partner"]
        .search(
            [
                ("is_supplier", "=", True),
                (
                    "ref",
                    "in",
                    [
                        "60425",  # agora_sana
                        "61645",  # ASP International
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
                            env.ref(
                                "alc_product_category_data.product_categ_materiel"
                            ).id,
                        )
                    ],
                    [
                        (
                            "categ_id",
                            "child_of",
                            env.ref("alc_product_food.product_categ_ali").id,
                        )
                    ],
                    [
                        (
                            "categ_id",
                            "child_of",
                            env.ref(
                                "alc_product_category_data.product_categ_parapharmacie"
                            ).id,
                        )
                    ],
                ]
            ),
            [("supplier_id", "not in", supplier_ids_to_exclude)],
        ]
    )
    assortment_filter.domain = str(domain)


def migrate(cr, version):
    _initialize_product_assortment_filter(cr)
