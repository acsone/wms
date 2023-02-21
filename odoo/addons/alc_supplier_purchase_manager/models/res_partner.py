# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):

    purchase_manager_id = fields.Many2one(
        comodel_name="res.users", string="Purchase manager"
    )

    substitute_purchase_manager_id = fields.Many2one(
        comodel_name="res.users", string="Substitute purchase manager"
    )
