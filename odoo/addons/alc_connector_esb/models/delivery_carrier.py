# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields

from odoo.addons.delivery.models import delivery_carrier


class DeliveryCarrier(delivery_carrier.DeliveryCarrier):

    esb_ref = fields.Char(string="Reference for ESB", copy=False)
