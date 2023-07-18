# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info("Define configuration for classification computations")
    cron = env.ref("product_abc_classification.ir_cron_product_abc_classification")
    cron.write(
        {
            "interval_type": "week",
            "interval_number": 1,
            "run_as_queue_job": True,
        }
    )
