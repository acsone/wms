# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """
    This will restore `Read Margin` group to users that have `Edit Costs` one.

    as in previous version.
    """
    cost_edit_group = env.ref("product_cost_security.group_product_edit_cost")
    group = env.ref("sale_margin_security.group_sale_margin_security")

    cost_edit_group.users.groups_id |= group

    _logger.info("Set `Read Margin` group to users in `Edit`for costs.")
