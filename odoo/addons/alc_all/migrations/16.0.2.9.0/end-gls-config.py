# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _add_gls_config(env):
    """Activate the option for 'Livraisons'."""
    out = env.ref("stock.picking_type_out")
    out.show_gls_put_in_pack_wizard = True


@openupgrade.migrate()
def migrate(env, version):
    _add_gls_config(env)
