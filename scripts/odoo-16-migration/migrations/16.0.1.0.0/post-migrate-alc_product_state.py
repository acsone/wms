# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # remove useless product.state records installed
    # by the module product_state
    env.ref("product_state.product_state_draft").unlink()
    env.ref("product_state.product_state_sellable").unlink()
    env.ref("product_state.product_state_end").unlink()
    env.ref("product_state.product_state_obsolete").unlink()
