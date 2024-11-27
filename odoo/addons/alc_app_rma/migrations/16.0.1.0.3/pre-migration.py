# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

logger = logging.getLogger(__name__)


def migrate(cr, version):
    logger.info("Mark module to uninstall")
    query = """
            UPDATE ir_module_module
                SET state = 'to remove'
                WHERE name = 'alc_rma_shipment_advice' AND state NOT IN ('uninstallable', 'uninstalled')
        """
    cr.execute(query)
