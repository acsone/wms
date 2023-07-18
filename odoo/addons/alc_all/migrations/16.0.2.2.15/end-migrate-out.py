# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info("Migrate output location under VLB")

    location_ids = [
        env.ref("stock.stock_location_output").id,
    ]
    location_vlb = env.ref("alc_stock_location_data.stock_location_vlb").id
    env["stock.location"].browse(location_ids).write({"location_id": location_vlb})
