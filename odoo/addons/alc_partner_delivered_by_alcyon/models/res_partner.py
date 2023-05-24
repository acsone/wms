# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.delivery.models.partner import ResPartner as Partner


class ResPartner(Partner):

    is_delivered_by_alcyon = fields.Boolean("Delivered by Alcyon?")
