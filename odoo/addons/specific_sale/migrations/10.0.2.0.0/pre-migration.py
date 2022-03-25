# -*- coding: utf-8 -*-
# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """
        delete from ir_ui_view where arch_db like '%last_suite_name%' and arch_fs like 'specific_sale%';
    """
    )
