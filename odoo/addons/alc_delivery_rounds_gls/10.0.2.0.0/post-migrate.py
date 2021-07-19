# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    gls_template_id = 128
    domain_instances = [
        ("itinerary_ids.template_ids", "=", gls_template_id),
        ("state", "=", "close"),
    ]
    instances = env["round.instance"].search(domain_instances)
    domain_pickings = [
        ("delivery_round_id", "in", instances.ids),
        ("state", "=", "done"),
        ("delivery_type", "=", "gls"),
        ("picking_type_code", "=", "outgoing"),
    ]
    pickings = env["stock.picking"].search(domain_pickings)
    customers = pickings.mapped("delivery_round_customer_id")
    customers.write({"delivered": True})
