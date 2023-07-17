# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info("Migrate parkings locations under Réceptions")

    location_ids = [
        env.ref("__setup__.stock_location_parking_ali").id,
        env.ref("__setup__.stock_location_parking_frigo").id,
        env.ref("__setup__.stock_location_parking_materiel").id,
        env.ref("__setup__.stock_location_parking_medoc").id,
    ]
    location_reception = env.ref("stock.stock_location_company").id
    env["stock.location"].browse(location_ids).write(
        {"location_id": location_reception}
    )
