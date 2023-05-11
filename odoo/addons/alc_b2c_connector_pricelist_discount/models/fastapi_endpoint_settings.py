# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.alc_b2c_connector.models.fastapi_endpoint_settings import (
    FastapiEndpointSettings as FastapiEndpointSettingsBase,
)
from odoo.addons.product.models.product_pricelist import Pricelist


class FastapiEndpointSettings(FastapiEndpointSettingsBase):
    discount_pricelist_id = fields.Many2one[Pricelist](string="Alcyon Discount")
