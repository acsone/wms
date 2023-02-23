# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _move_product_template(env):
    _logger.info("product.template: move fields 'sale_price_2' and 'indicated_price'")
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.template",
        [
            "sale_price_2",
            "indicated_price",
        ],
        "specific_product",
        "alc_product_additional_price",
    )


@openupgrade.migrate()
def migrate(env, version):
    _move_product_template(env)
