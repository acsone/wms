# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields

from odoo.addons.base.models.res_config import ResConfigSettings as SettingsBase


class ResConfigSettings(SettingsBase):

    # TODO: This should be removed when package category will be completely
    # migrated (data)
    delivery_slip_packages_display_mode = fields.Selection(
        related="company_id.delivery_slip_packages_display_mode",
        readonly=False,
    )
