# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.purchase_discount.models.res_partner import (
    ResPartner as ResPartnerBase,
)


class ResPartner(ResPartnerBase):

    supplier_discount = fields.Float("Supplier discount %")
