# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base.models.res_partner import PartnerCategory

from .res_partner import B2C_CUSTOMER_CATEGORY_REF


class ResPartnerCategory(PartnerCategory):
    def unlink(self):
        bc2_category = self.env.ref(B2C_CUSTOMER_CATEGORY_REF)
        if bc2_category in self:
            raise UserError(_("B2C category can't be removed."))
        return super().unlink()
