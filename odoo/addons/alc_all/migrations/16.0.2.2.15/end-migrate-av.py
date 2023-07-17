# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info(
        "Migrate achetés/vendus B-M5-AV locations under Achetés/vendus Médicaments"
    )

    location_ids = [
        env.ref("alc_stock_storage_type.location_M_B-M5-AV").id,
    ]
    location_av = env.ref("__setup__.stock_location_order_medoc").id
    env["stock.location"].browse(location_ids).write({"location_id": location_av})
