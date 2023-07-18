# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _migrate_quant_package(env):
    _logger.info("Remove pack type on some quant packages")

    quant_packages = env["stock.quant.package"].search(
        [
            ("location_id", "=", False),
            ("package_type_id", "!=", False),
            ("package_type_id.package_carrier_type", "!=", "GLS"),
        ]
    )
    quant_packages.write({"package_type_id": False})


@openupgrade.migrate()
def migrate(env, version):
    _migrate_quant_package(env)
