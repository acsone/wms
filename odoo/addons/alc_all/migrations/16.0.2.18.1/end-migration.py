# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

logger = logging.getLogger(__name__)


def migrate(cr, version):
    logger.info("Disable session store on fastapi")
    cr.execute("UPDATE fastapi_endpoint set save_http_session = false")
