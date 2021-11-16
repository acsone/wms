# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.update_module_moved_fields(
        cr,
        "res.partner",
        ["vet_depot_number", "vet_subscription_number"],
        "specific_partner",
        "alc_partner_veterinary",
    )
