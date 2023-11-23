# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade


def migrate(cr, version):
    openupgrade.update_module_moved_fields(
        cr,
        "ir.sequence",
        ["use_end_date"],
        "ir_sequence_period",
        "alc_ir_sequence_period",
    )
