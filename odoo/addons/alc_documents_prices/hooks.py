# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    cr.execute("SELECT id FROM res_partner ORDER BY id DESC LIMIT 1;")
    max_id = cr.fetchall()[0][0]
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.partner"].search([])._migrate_jobify_process_dossier(0, max_id, 1000)
