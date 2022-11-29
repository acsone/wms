# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return
    # doesn't work in mig, component cannot be initialized
    # this has to be launched manually then...
    # env = api.Environment(cr, SUPERUSER_ID, {})
    # env["se.backend.elasticsearch"].cron_synchronize_ads()
