# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models.res_partner import ResPartner as ResPartnerBase


class ResPartner(ResPartnerBase):

    manual_sale_order_allowed = fields.Boolean(index=True)
