# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import uuid

from odoo import api, models
from odoo.tools.config import config as system_base_config

_logger = logging.getLogger(__name__)


class AlcRunningEnvRegistration(models.AbstractModel):

    _name = "alc.running.env.registration"
    _description = "Alc Running Env Registration"

    @api.model_cr
    def _register_hook(self):
        """
        Cleanup database to avoid issue with copy of production databases
        """
        if system_base_config.get("running_env", "prod").lower() == "prod":
            return

        IrConfigParameter = self.env["ir.config_parameter"]

        enterprise_code = IrConfigParameter.get_param("database.enterprise_code")
        if enterprise_code:
            db_uuid = IrConfigParameter.get_param("database.uuid")
            _logger.warning(
                "Reset enterprise code %s and db uid %s", enterprise_code, db_uuid
            )
            # reset enterprise keys and db uuid
            self.env.cr.execute(
                """
                DELETE FROM ir_config_parameter
                WHERE key = 'database.enterprise_code';

                UPDATE ir_config_parameter
                SET value = 'copy'
                WHERE key = 'database.expiration_reason'
                AND value != 'demo';

                UPDATE ir_config_parameter
                SET value = CURRENT_DATE + INTERVAL '2 month'
                WHERE key = 'database.expiration_date';

                UPDATE ir_config_parameter
                SET value = %s
                WHERE key = 'database.uuid';
            """,
                (str(uuid.uuid1()),),
            )
