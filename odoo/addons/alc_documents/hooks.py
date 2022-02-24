# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    # we don't filter attachments; of about 1.6*10^6 attachments,
    # 1.5*10^6 should be checked, so it is not worth the complexity
    cr.execute("SELECT id FROM ir_attachment ORDER BY id DESC LIMIT 1;")
    max_id = cr.fetchall()[0][0]
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.attachment"]._migrate_jobify_process_dossier(0, max_id, 1000)
