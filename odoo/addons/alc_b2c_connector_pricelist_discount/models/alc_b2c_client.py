# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.alc_b2c_connector.models.alc_b2c_client import (
    AlcB2cClient as AlcB2cClientBase,
)
from odoo.addons.product.models.product_pricelist import Pricelist


class AlcB2cClient(AlcB2cClientBase):
    discount_pricelist_id = fields.Many2one[Pricelist](string="Alcyon Discount")
