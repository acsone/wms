# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.base.models.res_users import Users


class ResPartner(Partner):

    purchase_manager_id = fields.Many2one[Users](string="Purchase manager")

    substitute_purchase_manager_id = fields.Many2one[Users](
        string="Substitute purchase manager"
    )
