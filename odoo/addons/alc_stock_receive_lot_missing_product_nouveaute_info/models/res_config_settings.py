# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    reception_wizard_constraints = fields.Boolean(
        "Reception Wizard Constraints",
        default=False,
        config_parameter="reception_wizard_constraints",
    )
