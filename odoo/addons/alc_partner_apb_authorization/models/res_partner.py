# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner as BasePartner


class ResPartner(BasePartner):

    apb_authorization = fields.Char(string="Authorization/APB")
