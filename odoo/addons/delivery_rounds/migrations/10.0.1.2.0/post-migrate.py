# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    instances_open = env["round.instance"].search([("state", "!=", "done")])
    domain_customers = [("delivery_round_id", "in", instances_open.ids)]
    env["round.instance.customer"].search(domain_customers)._compute_delivered()
