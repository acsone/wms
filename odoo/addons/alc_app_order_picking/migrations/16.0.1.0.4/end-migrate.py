# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Merge the package type Nouveaute")

    xmlids_spec = [
        (
            "alc_stock_storage_type.package_st_M_M_Nouveaute",
            "alc_product_is_new.package_st_M_M_Nouveaute",
        )
    ]

    openupgrade.rename_xmlids(env.cr, xmlids_spec, allow_merge=True)
