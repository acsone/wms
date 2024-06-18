# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Create new columns for old role names."""

    cr.execute(
        """
        ALTER TABLE product_pricelist
        ADD COLUMN old_role_name VARCHAR,
        ADD COLUMN old_discount_role_name VARCHAR
        """
    )
    cr.execute(
        """
        UPDATE product_pricelist
        SET old_role_name = role_name,
            old_discount_role_name = discount_role_name
        """
    )

    # recompute the role names
    cr.execute(
        """
        UPDATE product_pricelist
        SET role_name = 'p' || id,
            discount_role_name = 'd' || id
        """
    )
