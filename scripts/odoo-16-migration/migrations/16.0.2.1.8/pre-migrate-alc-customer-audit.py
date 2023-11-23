# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

field_renames = [
    ("res.partner", "res_partner", "no_delivery_round", "no_release_channel"),
]


def migrate(cr, version):
    openupgrade.rename_fields(cr, field_renames)
