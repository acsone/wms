# -*- coding: utf-8 -*-
# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """
        delete from ir_ui_view where arch_db like '%veterinary_group_ids%' and arch_fs like 'alc_partner_veterinary%';
    """
    )
