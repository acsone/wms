# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Set long term carrier flag")
    cr.execute(
        """
        UPDATE delivery_carrier dc
        SET is_long_term_delivery = TRUE
        WHERE dc.id = (SELECT res_id FROM ir_model_data
                       WHERE model LIKE 'delivery.carrier'
                       AND name LIKE 'deliver_carrier_long_term')
    """
    )
