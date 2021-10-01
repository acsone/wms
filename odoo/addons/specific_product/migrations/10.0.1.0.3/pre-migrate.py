# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # cleaup view where moved fields where previously declared...
    cr.execute(
        "delete from ir_ui_view where arch_db like '%veterinary_only%' or "
        "arch_db like '%belgium_only%' or arch_db like '%cnk_code%'"
    )
