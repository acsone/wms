# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import migrate_translations_to_jsonb


@openupgrade.migrate()
def migrate(env, version):
    missing_translations = [
        ("product.template", "description_shop_short"),
        ("product.template", "description_shop_long"),
    ]
    migrate_translations_to_jsonb(env, missing_translations)
