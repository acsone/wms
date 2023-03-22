# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields

from odoo.addons.stock.models.stock_location import Location as LocationBase


class Location(LocationBase):

    is_reception_wizard = fields.Boolean("Visible in reception wizard")
